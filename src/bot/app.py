# pyright: ignore-all-errors
# -- pyright: reportMissingImports=false, reportGeneralTypeIssues=false, reportUnknownMemberType=false, reportOptionalMemberAccess=false, reportAttributeAccessIssue=false
# --- START OF DEFINITIVE BUILD ---
# ruff: noqa
# pylint: disable=all
# mypy: ignore-errors
# pyright: reportMissingTypeStubs=false, reportUnusedImport=false, reportConstantRedefinition=false
import json
import logging
import os
import html
import traceback
from pathlib import Path
from typing import cast, Dict, Any
import urllib.parse
import datetime
import uuid
import random # Added for training mode
import base64

import joblib
import pandas as pd
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
    Message,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.core.data_loader import UniversityDataManager
from src.core.recommender import Recommender
from src.core.major_profiles import load_major_profiles
from src.core.ml_models.admission_model import load_model as load_admission_model
from src.core.user_profile_manager import save_user_profile, get_user_profile
try:
    from src.core.career_data import CAREER_PATHS  # noqa: WPS433
except ImportError:  # pragma: no cover
    CAREER_PATHS = {}

# ---------------------------------------------------------------------------
# Logging & dotenv
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
load_dotenv()

# ---------------------------------------------------------------------------
# URL Configuration – served by run.sh (ngrok + http.server on port 8000)
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("NGROK_URL")  # Set at runtime by run.sh
QUIZ_WEB_APP_URL = f"{BASE_URL}/web_templates/quiz/index.html" if BASE_URL else ""
BROWSER_WEB_APP_URL = f"{BASE_URL}/web_templates/browser/index.html" if BASE_URL else ""
CALCULATOR_WEB_APP_URL = f"{BASE_URL}/web_templates/calculator/index.html" if BASE_URL else ""
DNA_WEB_APP_URL = f"{BASE_URL}/web_templates/dna/index.html" if BASE_URL else ""
VAULT_WEB_APP_URL = f"{BASE_URL}/web_templates/vault/index.html" if BASE_URL else ""

# ---------------------------------------------------------------------------
# UI – Main Menu
# ---------------------------------------------------------------------------

def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🧬 វិភាគ DNA និស្សិត", callback_data="launch_quiz")],
        [InlineKeyboardButton("📚 បញ្ជីសាកលវិទ្យាល័យ", callback_data="launch_browser")],
        [InlineKeyboardButton("🚀 អំពីអាជីពការងារ", callback_data="career_start")],
        [InlineKeyboardButton("💰 គណនាថ្លៃសិក្សា", callback_data="launch_calculator")],
        [InlineKeyboardButton("🗂️ ត្រៀមឯកសារ", callback_data="launch_vault")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ---------------------------------------------------------------------------
# Command / Callback Handlers
# ---------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start – Show main menu and welcome returning users."""
    if update.message is None:
        return
    msg = cast(Message, update.message)
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name if msg.from_user else ""

    user_data = get_user_profile(user_id)
    user_profile = user_data.get('profile') if user_data else None

    if user_profile:
        welcome_message = f"Welcome back, {first_name}! It's great to see you again."
        await msg.reply_text(welcome_message)
    else:
        welcome_message = f"Hi {first_name}! Welcome to your University Co-Pilot. I'm here to help you figure out your next big step."
        await msg.reply_text(welcome_message, reply_markup=ReplyKeyboardRemove())
    
    await msg.reply_text(
        text="នេះគឺជាផ្ទាំងគ្រប់គ្រងរបស់អ្នក។\n\n**សូមជ្រើសរើសឧបករណ៍៖**",
        reply_markup=build_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def all_button_press_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Single router for all inline-button presses."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    choice = query.data or ""

    # -------------------------------------------------------------------
    # Launch Web-Apps
    # -------------------------------------------------------------------
    if choice.startswith("launch_"):
        if not BASE_URL:
            msg_err = cast(Message, query.message)
            await msg_err.reply_text(
                "⛔ ERROR: Web App server is not running. Please start the bot using run.sh."
            )  # type: ignore[attr-defined]
            return

        app_name = choice.split("_", 1)[1]
        url_map = {
            "quiz": QUIZ_WEB_APP_URL,
            "browser": BROWSER_WEB_APP_URL,
            "calculator": CALCULATOR_WEB_APP_URL,
            "vault": VAULT_WEB_APP_URL,
        }
        button_text_map = {
            "quiz": "🔬 បើកការវិភាគ",
            "browser": "📚 បើកបញ្ជី",
            "calculator": "💰 បើកការគណនា",
            "vault": "🗂️ បើកការត្រៀមឯកសារ",
        }
        url = url_map.get(app_name, "")
        button_text = button_text_map.get(app_name, "Open App")

        msg_open = cast(Message, query.message)
        await msg_open.reply_text(
            "ចុចប៊ូតុងខាងក្រោមដើម្បីបើក៖",
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(text=button_text, web_app=WebAppInfo(url=url)),
                resize_keyboard=True,
            ),
        )  # type: ignore[attr-defined]
        return

    # -------------------------------------------------------------------
    # University-specific Actions
    # -------------------------------------------------------------------
    if choice.startswith("calc_uni_"):
        university_id = int(choice.split("_")[-1])
        data_manager = context.application.bot_data.get("data_manager")
        if data_manager:
            university = data_manager.get_university_by_id(university_id)
            if university:
                # Pre-fill calculator with university's tuition fees
                fees = university.get('tuition_fees', {})
                min_fee = fees.get('range_min', 0)
                calc_url = f"{CALCULATOR_WEB_APP_URL}?prefill_tuition={min_fee}&uni_name={university.get('name_km', '')}"

                keyboard = [[InlineKeyboardButton("💰 បើកការគណនា", web_app=WebAppInfo(url=calc_url))]]
                await query.edit_message_text(
                    f"គណនាថ្លៃសិក្សាសម្រាប់ {university.get('name_km', 'សាកលវិទ្យាល័យនេះ')}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        return

    if choice.startswith("docs_uni_"):
        university_id = int(choice.split("_")[-1])
        data_manager = context.application.bot_data.get("data_manager")
        if data_manager:
            university = data_manager.get_university_by_id(university_id)
            if university and query.message:
                # Show admission requirements
                requirements = university.get('admission_requirements_km', [])
                response_lines = [f"📋 *ឯកសារចាំបាច់សម្រាប់ {university.get('name_km', 'សាកលវិទ្យាល័យនេះ')}:*\n"]

                if requirements:
                    for i, req in enumerate(requirements, 1):
                        response_lines.append(f"{i}. {req}")
                else:
                    response_lines.append("• សញ្ញាបត្រមធ្យមសិក្សាទុតិយភូមិ")
                    response_lines.append("• ពាក្យស្នើសុំចូលរៀន")
                    response_lines.append("• រូបថត")
                    response_lines.append("• ប្រតិបត្តិរូប")

                response_lines.append(f"\n📞 *ទំនាក់ទំនងសម្រាប់ព័ត៌មានបន្ថែម:*")
                contact = university.get('contact', {})
                if contact.get('phones'):
                    response_lines.append(f"ទូរស័ព្ទ: {', '.join(contact['phones'])}")
                if contact.get('email'):
                    response_lines.append(f"អ៊ីមែល: {contact['email']}")

                keyboard = [
                    [InlineKeyboardButton("🗂️ បើកការត្រៀមឯកសារ", callback_data="launch_vault")],
                    [InlineKeyboardButton("⬅️ ត្រលប់ទៅសាកលវិទ្យាល័យ", callback_data=f"uni_detail_{university_id}")]
                ]

                await query.edit_message_text(
                    "\n".join(response_lines),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        return

    if choice.startswith("uni_detail_"):
        university_id = int(choice.split("_")[-1])
        data_manager = context.application.bot_data.get("data_manager")
        if data_manager:
            university = data_manager.get_university_by_id(university_id)
            if university:
                # Build detailed university information (same as in web_app_data_handler)
                response_lines = [f"🏫 *{university.get('name_km', 'N/A')}*"]
                response_lines.append(f"📍 *ទីតាំង:* {university.get('location', 'N/A')}")
                response_lines.append(f"🏛️ *ប្រភេទ:* {university.get('type', 'N/A')}")
                response_lines.append(f"📅 *ឆ្នាំបង្កើត:* {university.get('established_year', 'N/A')}")

                # Tuition fees
                fees = university.get('tuition_fees', {})
                if fees:
                    fee_range = f"${fees.get('range_min', 0)} - ${fees.get('range_max', 0)}"
                    response_lines.append(f"💰 *ថ្លៃសិក្សា:* {fee_range}/ឆ្នាំ")

                # Faculties and majors
                faculties = university.get('faculties', [])
                if faculties:
                    response_lines.append(f"\n📚 *មហាវិទ្យាល័យ និងជំនាញ:*")
                    for faculty in faculties[:3]:  # Show first 3 faculties
                        faculty_name = faculty.get('name_km', 'N/A')
                        majors = faculty.get('majors', [])
                        if majors:
                            major_names = [m.get('name_km', 'N/A') for m in majors[:3]]
                            response_lines.append(f"• *{faculty_name}:* {', '.join(major_names)}")
                            if len(majors) > 3:
                                response_lines.append(f"  ... និង {len(majors) - 3} ជំនាញផ្សេងទៀត")

                # Contact information
                contact = university.get('contact', {})
                if contact:
                    response_lines.append(f"\n📞 *ព័ត៌មានទំនាក់ទំនង:*")
                    if contact.get('phones'):
                        response_lines.append(f"• ទូរស័ព្ទ: {', '.join(contact['phones'])}")
                    if contact.get('email'):
                        response_lines.append(f"• អ៊ីមែល: {contact['email']}")
                    if contact.get('website'):
                        response_lines.append(f"• គេហទំព័រ: {contact['website']}")

                # Create action buttons
                keyboard = [
                    [InlineKeyboardButton("💰 គណនាថ្លៃសិក្សា", callback_data=f"calc_uni_{university_id}")],
                    [InlineKeyboardButton("📋 ត្រៀមឯកសារចូលរៀន", callback_data=f"docs_uni_{university_id}")],
                    [InlineKeyboardButton("📤 ចែករំលែកព័ត៌មាន", callback_data=f"share_uni_{university_id}")],
                    [InlineKeyboardButton("⬅️ ត្រលប់ទៅបញ្ជី", callback_data="launch_browser")]
                ]

                await query.edit_message_text(
                    "\n".join(response_lines),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        return

    if choice.startswith("share_uni_"):
        university_id = int(choice.split("_")[-1])
        data_manager = context.application.bot_data.get("data_manager")
        if data_manager:
            university = data_manager.get_university_by_id(university_id)
            if university:
                # Create shareable university summary
                share_text = f"""🏫 {university.get('name_km', 'N/A')} ({university.get('name_en', 'N/A')})

📍 ទីតាំង: {university.get('location', 'N/A')}
💰 ថ្លៃសិក្សា: ${university.get('tuition_fees', {}).get('range_min', 0)} - ${university.get('tuition_fees', {}).get('range_max', 0)}/ឆ្នាំ
🏛️ ប្រភេទ: {university.get('type', 'N/A')}

📞 ទំនាក់ទំនង:"""

                contact = university.get('contact', {})
                if contact.get('phones'):
                    share_text += f"\n• ទូរស័ព្ទ: {', '.join(contact['phones'])}"
                if contact.get('website'):
                    share_text += f"\n• គេហទំព័រ: {contact['website']}"

                share_text += "\n\n📚 ស្វែងរកព័ត៌ព័មានបន្ថែមតាម @EduGuideKhBot"

                keyboard = [
                    [InlineKeyboardButton("📋 ចម្លងអត្ថបទ", callback_data=f"copy_text")],
                    [InlineKeyboardButton("⬅️ ត្រលប់ទៅសាកលវិទ្យាល័យ", callback_data=f"uni_detail_{university_id}")]
                ]

                await query.edit_message_text(
                    share_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        return

    if choice == "ask_question":
        await query.edit_message_text(
            "Please type your question. I'll do my best to answer!"
        )
        return

    if choice == "find_scholarships":
        await query.edit_message_text(
            "Many universities offer scholarships! You can find specific scholarship information on each university's detailed page, or visit their official websites for more details."
        )
        return

    # -------------------------------------------------------------------
    # Career Explorer
    # -------------------------------------------------------------------
    if choice in {"career_start", "back_to_career"}:
        major_keys = list(CAREER_PATHS.keys())
        keyboard = [
            [InlineKeyboardButton(key, callback_data=f"career_show:{key}")]
            for key in major_keys
        ]
        keyboard.append(
            [InlineKeyboardButton("⬅️ ត្រឡប់ទៅកាន់ទំព័រដើម", callback_data="back_to_main")]
        )
        await query.edit_message_text(
            "សូមជ្រើសរើសវិស័យដែលអ្នកចាប់អារម្មណ៍៖",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if choice.startswith("career_show:"):
        major_key = choice.split(":", 1)[1]
        info = CAREER_PATHS.get(major_key, {})
        if not info:
            await query.answer("No data available.")
            return
        content = (
            f"*{info['title']}*\n\n"
            f"**{info['entry_level']['title']}**\n  - តួនាទី: {info['entry_level']['roles']}\n  - ប្រាក់ខែ: {info['entry_level']['salary']}\n\n"
            f"**{info['mid_level']['title']}**\n  - តួនាទី: {info['mid_level']['roles']}\n  - ប្រាក់ខែ: {info['mid_level']['salary']}\n\n"
            f"**{info['senior_level']['title']}**\n  - តួនាទី: {info['senior_level']['roles']}\n  - ប្រាក់ខែ: {info['senior_level']['salary']}\n\n"
            f"**និន្នាការអនាគត:** {info['future_trend']}"
        )

        # ---------------------------------------------------------------
        # Suggest relevant universities for the selected career field
        # ---------------------------------------------------------------
        try:
            data_manager = context.application.bot_data.get("data_manager")
            if data_manager is not None:
                universities = data_manager.get_all_universities()
                matched = []
                for uni in universities:
                    for faculty in uni.get("faculties", []):
                        for major in faculty.get("majors", []):
                            if major.get("category_km") == major_key:
                                matched.append(uni)
                                break
                        if matched and matched[-1] is uni:
                            break
                # take up to 3 matches, prefer those with higher ranking_score if exists
                matched_sorted = sorted(
                    matched,
                    key=lambda u: u.get("ranking_score", 0),
                    reverse=True,
                )[:3]
                if matched_sorted:
                    uni_lines = ["\n🏫 *សាកលវិទ្យាល័យកំពើរដែលផ្តល់ជម្រើសខាងលើ:*"]
                    for u in matched_sorted:
                        uni_lines.append(f"• {u.get('name_km')} ({u.get('location')})")
                    content += "\n" + "\n".join(uni_lines)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to attach university suggestions: %s", exc)

        await query.edit_message_text(
            content,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ ថយក្រោយ", callback_data="career_start")]]
            ),
        )
        return

    # -------------------------------------------------------------------
    # Back to main
    # -------------------------------------------------------------------
    if choice == "back_to_main":
        await query.edit_message_text(
            "នេះគឺជាផ្ទាំងគ្រប់គ្រងរបស់អ្នក។\n\n**សូមជ្រើសរើសឧបករណ៍៖**",
            reply_markup=build_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )


# ---------------------------------------------------------------------------
# Web-App Data Handler
# ---------------------------------------------------------------------------
def _build_dna_url(base_url: str, recommendations: list, user_profile: dict, max_score: int) -> str:
    """Builds the URL for the DNA web app with encoded parameters."""
    params = {
        "recommendations": json.dumps(recommendations),
        "user_profile": json.dumps(user_profile),
        "max_score": float(max_score) # Ensure max_score is a float
    }
    encoded_params = base64.urlsafe_b64encode(json.dumps(params).encode()).decode()
    return f"{base_url}?data={encoded_params}"


async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles data received from any of the web apps."""
    if not update.message or not update.message.web_app_data:
        return

    msg = cast(Message, update.message)
    user_id = msg.from_user.id
    try:
        data_str = msg.web_app_data.data
        logger.info(f"Received Web App data: {data_str}")
        data = json.loads(data_str)
        source = data.get("source")

        recommender = context.application.bot_data.get("recommender")
        if not recommender:
            logger.error("Recommender not initialized.")
            await msg.reply_text("An error occurred. Please try again later.")
            return

        if source == "quiz":
            user_profile = _build_user_profile_from_quiz(data)
            save_user_profile(user_id, user_profile)
            context.user_data["profile"] = user_profile
            
            recommended_majors, max_score = recommender.get_major_recommendations(user_profile)

            if recommended_majors:
                dna_url = _build_dna_url(DNA_WEB_APP_URL, recommended_majors, user_profile, max_score)

                await msg.reply_text(
                    "✅ *Your DNA analysis is complete!*\n\nHere are your top 3 recommended majors:",
                    parse_mode=ParseMode.MARKDOWN,
                )
                await msg.reply_text(
                    "Click the button below to see your detailed results and find matching universities:",
                    reply_markup=ReplyKeyboardMarkup.from_button(
                        KeyboardButton(text="🧬 Open DNA Results", web_app=WebAppInfo(url=dna_url)),
                        resize_keyboard=True,
                    ),
                )

        elif source == "dna_university_request":
            user_data = get_user_profile(user_id)
            user_profile = user_data.get('profile') if user_data else None
            major_name_en = data.get("major_name_en")
            if not user_profile or not major_name_en:
                await msg.reply_text("Missing data to get university recommendations. Please try the quiz again.")
                return

            uni_recs = recommender.get_university_recommendations(major_name_en, user_profile)

            if not uni_recs:
                await msg.reply_text(
                    f"I couldn't find any universities that are a great fit for both your profile and the {major_name_en} major. Try exploring other majors!"
                )
                return

            response_lines = [f"🏫 *Recommended Universities for {major_name_en}:*\n"]
            for rec in uni_recs:
                 response_lines.append(f"• *{rec['university_name']}* (Score: {rec['score']:.0f})\n_{rec['details']}_")
            
            keyboard = [
                [InlineKeyboardButton("🔍 Tell me more about a University", callback_data="launch_browser")],
                [InlineKeyboardButton("💰 Find Scholarships", callback_data="find_scholarships")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main")]
            ]

            await msg.reply_text(
                "\n".join(response_lines),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif source == "catalog":
            university_id = data.get("university_id")
            if not university_id:
                await msg.reply_text("Could not find the specified university.")
                return

            data_manager = context.application.bot_data.get("data_manager")
            university = data_manager.get_university_by_id(university_id)
            if not university:
                await msg.reply_text("Could not find the specified university.")
                return

            # Build detailed university information
            response_lines = [f"🏫 *{university.get('name_km', 'N/A')}*"]
            response_lines.append(f"📍 *Location:* {university.get('location', 'N/A')}")
            response_lines.append(f"🏛️ *Type:* {university.get('type', 'N/A')}")
            response_lines.append(f"📅 *Established:* {university.get('established_year', 'N/A')}")
            response_lines.append(f"💰 *Tuition:* ${university.get('tuition_fees', {}).get('range_min', 0)} - ${university.get('tuition_fees', {}).get('range_max', 0)}/year")
            response_lines.append(f"🎓 *Scholarships:* {university.get('scholarship_info_km', 'N/A')}")

            keyboard = [
                [InlineKeyboardButton("💰 Calculate Tuition", callback_data=f"calc_uni_{university_id}")],
                [InlineKeyboardButton("📋 Admission Requirements", callback_data=f"docs_uni_{university_id}")],
                [InlineKeyboardButton("⬅️ Back to List", callback_data="launch_browser")]
            ]

            await msg.reply_text(
                "\n".join(response_lines),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Error processing web app data: {e}")
        await msg.reply_text("There was an error processing your request from the web app.")


# ---------------------------------------------------------------------------
# Error Handler
# ---------------------------------------------------------------------------
async def error_handler(update: Update | None, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else to get the full context
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python traceback as a list of strings
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about the update
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Send the message
    if update:
        if update.callback_query:
            await context.bot.send_message(
                chat_id=update.callback_query.message.chat_id, text=message, parse_mode=ParseMode.HTML
            )
        elif update.message:
            await context.bot.send_message(
                chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML
            )
        else:
            # Fallback if update is not None but has no message or callback_query
            await context.bot.send_message(
                chat_id=context.bot_data.get("admin_chat_id", None) or update.effective_chat.id, # type: ignore
                text=message, parse_mode=ParseMode.HTML
            )
    else:
        # If update is None, send to a predefined admin chat ID or log only
        if "admin_chat_id" in context.bot_data:
            await context.bot.send_message(
                chat_id=context.bot_data["admin_chat_id"], text=message, parse_mode=ParseMode.HTML
            )
        else:
            logger.error("No chat ID available to send error message.")


# ---------------------------------------------------------------------------
# Feedback Handler
# ---------------------------------------------------------------------------
async def handle_text_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles natural language queries from the user."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.lower()
    user_id = update.message.from_user.id
    user_data = get_user_profile(user_id)
    user_profile = user_data.get('profile') if user_data else None

    if not user_profile:
        await update.message.reply_text("Please complete the DNA quiz first so I can give you personalized recommendations.")
        return

    # Simple keyword-based routing for now
    if "compare" in user_text and "universities" in user_text:
        # Extract university names (this is a simplified example)
        # A more robust solution would use NLP to extract entities
        words = user_text.split()
        uni_names = [word.upper() for word in words if word.upper() in [uni['name_short'] for uni in context.application.bot_data['data_manager'].get_all_universities()]]
        if len(uni_names) == 2:
            await compare_universities(update, context, uni_names[0], uni_names[1])
        else:
            await update.message.reply_text("Please tell me which two universities you'd like to compare (e.g., 'compare RUPP and ITC').")
    elif "show" in user_text and "universities" in user_text:
        await handle_university_query(update, context, user_text)
    else:
        await update.message.reply_text("I'm still learning to understand everything. Try asking me to 'compare RUPP and ITC' or 'show me universities in Phnom Penh for business'.")

async def compare_universities(update: Update, context: ContextTypes.DEFAULT_TYPE, uni1_short_name: str, uni2_short_name: str) -> None:
    """Compares two universities based on key metrics."""
    data_manager = context.application.bot_data.get("data_manager")
    uni1 = next((uni for uni in data_manager.get_all_universities() if uni['name_short'] == uni1_short_name), None)
    uni2 = next((uni for uni in data_manager.get_all_universities() if uni['name_short'] == uni2_short_name), None)

    if not uni1 or not uni2:
        await update.message.reply_text("I couldn't find one of the universities you mentioned.")
        return

    response = f"**Comparison: {uni1['name_en']} vs. {uni2['name_en']}**\n\n"
    response += f"**Ranking Score:** {uni1['ranking_score']} vs. {uni2['ranking_score']}\n"
    response += f"**Tuition:** ${uni1['tuition_fees']['range_min']}-${uni1['tuition_fees']['range_max']} vs. ${uni2['tuition_fees']['range_min']}-${uni2['tuition_fees']['range_max']}\n"
    response += f"**Total Majors:** {uni1['total_majors']} vs. {uni2['total_majors']}\n"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def handle_university_query(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str) -> None:
    """Handles queries for universities based on location and major."""
    data_manager = context.application.bot_data.get("data_manager")
    universities = data_manager.get_all_universities()

    # Simplified entity extraction
    location = None
    major_category = None

    for loc in ["phnom penh", "siem reap", "battambang"]:
        if loc in query:
            location = loc.title()
    
    for cat in context.application.bot_data['recommender'].major_profiles['major_category'].unique():
        if cat.lower() in query:
            major_category = cat

    if location:
        universities = [uni for uni in universities if uni['location'] == location]
    if major_category:
        universities = [uni for uni in universities if major_category in uni['major_categories_en']]

    if not universities:
        await update.message.reply_text("I couldn't find any universities matching your criteria.")
        return

    response = "**Here are some universities that match your query:**\n\n"
    for uni in universities[:5]: # Limit to 5 results
        response += f"- **{uni['name_en']}** ({uni['location']})\n"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


# ---------------------------------------------------------------------------
# Training Mode Handler
# ---------------------------------------------------------------------------
async def train_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts a training session by presenting a synthetic user profile for feedback."""
    if not update.message:
        return

    try:
        with open("data/synthetic_quiz_profiles.jsonl", "r", encoding="utf-8") as f:
            all_profiles = [json.loads(line) for line in f]

        judged_profiles_str = set()
        try:
            with open("data/feedback.jsonl", "r", encoding="utf-8") as f:
                for line in f:
                    feedback_data = json.loads(line)
                    judged_profiles_str.add(json.dumps(feedback_data['user_profile']['answers'], sort_keys=True))
        except FileNotFoundError:
            pass

        unjudged_profile = None
        random.shuffle(all_profiles)
        for profile in all_profiles:
            profile_str = json.dumps(profile['answers'], sort_keys=True)
            if profile_str not in judged_profiles_str:
                unjudged_profile = profile
                break

        if not unjudged_profile:
            await update.message.reply_text("🎉 All synthetic profiles have been reviewed!")
            return

        user_profile_data = unjudged_profile['answers']

        recommender: Recommender = context.application.bot_data["recommender"]
        major_recommendations, _ = recommender.get_major_recommendations(user_profile_data, top_n=3)

        if not major_recommendations:
            await update.message.reply_text("Could not generate a major recommendation for this profile.")
            return

        primary_major = major_recommendations[0]["major_name_en"]
        university_recommendations = recommender.get_university_recommendations(
            major_name_en=primary_major,
            user_profile=user_profile_data,
            top_n=3
        )

        profile_summary = [f"*{key.replace('_', ' ').title()}:* {', '.join(val) if isinstance(val, list) else val}" for key, val in user_profile_data.items()]
        reco_summary = [f"{i+1}. *{reco['university_name']}* (Score: {reco['score']:.0f})" for i, reco in enumerate(university_recommendations)]

        response_text = (
            f"--- 🎓 Training Mode ---\n\n"
            f"Persona: *{unjudged_profile['persona']}* | Profile:\n"
            f"{' | '.join(profile_summary)}\n\n"
            f"Bot Recommendation:\n"
            f"{'\n'.join(reco_summary)}\n\n"
            f"*Is this a good recommendation?*"
        )
        
        recommendation_id = str(uuid.uuid4())
        context.bot_data[recommendation_id] = {
            "user_profile": unjudged_profile,
            "recommendations": university_recommendations
        }
        feedback_keyboard = [
            InlineKeyboardButton("👍 Good Reco", callback_data=f"feedback:good:{recommendation_id}"),
            InlineKeyboardButton("👎 Bad Reco", callback_data=f"feedback:bad:{recommendation_id}")
        ]
        
        await update.message.reply_text(
            response_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([feedback_keyboard])
        )
    except Exception as e:
        logger.error(f"Error in /train command: {e}", exc_info=True)
        await update.message.reply_text("An error occurred during training.")

# ---------------------------------------------------------------------------
# Feedback Handler for Training Mode
# ---------------------------------------------------------------------------
async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles feedback from training mode."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    try:
        _, feedback_type, recommendation_id = query.data.split(":")

        # Get the stored recommendation data
        recommendation_data = context.bot_data.get(recommendation_id)
        if not recommendation_data:
            await query.edit_message_text("❌ Feedback session expired. Please try again.")
            return

        # Save feedback to file
        feedback_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "feedback": feedback_type,
            "user_profile": recommendation_data["user_profile"],
            "recommendations": recommendation_data["recommendations"]
        }

        with open("data/feedback.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        # Clean up stored data
        del context.bot_data[recommendation_id]

        feedback_emoji = "👍" if feedback_type == "good" else "👎"
        await query.edit_message_text(
            f"{feedback_emoji} Thank you for your feedback! This helps improve the recommendation system."
        )

    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        await query.edit_message_text("❌ Error processing feedback.")

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
def main() -> None:  # pragma: no cover
    """Entry point."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("FATAL: TELEGRAM_BOT_TOKEN environment variable not set.")

    # Load Data and Models
    data_manager = UniversityDataManager(data_path="data/data.json")
    major_profiles = load_major_profiles()
    admission_model = load_admission_model()

    # Initialize Application
    application = Application.builder().token(token).build()

    # Store the data manager and recommender in the application context
    application.bot_data.update({
        "data_manager": data_manager,
        "recommender": Recommender(
            universities=data_manager.get_all_universities(),
            major_profiles=major_profiles,
            admission_model=admission_model
        )
    })

    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("train", train_command))
    application.add_handler(CallbackQueryHandler(all_button_press_router))
    application.add_handler(CallbackQueryHandler(feedback_handler, pattern="^feedback:"))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_query))

    # Add error handler
    application.add_error_handler(error_handler)

    logger.info("--- Starting EduGuideBot ---")
    application.run_polling()


def _build_user_profile_from_quiz(quiz_ans: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms the raw dictionary from the web app quiz into the structured
    user profile dictionary that the recommender system expects.
    """
    # This function now acts as a simple pass-through and validation layer.
    # The recommender is responsible for handling the raw string values.

    # Mappings from Khmer to English for quiz answers
    study_format_map = {
        "ការបង្រៀន": "Lecture-based",
        "ការអនុវត្ត": "Practical/Hands-on",
        "ការងារជាក្រុម": "Group work",
        "ការស្រាវជ្រាវ": "Research-focused",
    }

    work_style_map = {
        "ម្នាក់ឯង": "Independent",
        "ជាក្រុម": "Team-oriented",
        "ជាអ្នកដឹកនាំ": "Leadership",
        "ជាអ្នកតាម": "Supportive",
    }

    company_type_map = {
        "ក្រុមហ៊ុនបច្ចេកវិទ្យាថ្មី (Startup)": "Startup",
        "ឯកជន": "Private Company",
        "រដ្ឋាភិបាល": "Government",
        "អង្គការមិនស្វែងរកប្រាក់ចំណេញ": "Non-profit",
        "ក្រុមហ៊ុនធំ": "Large Corporation",
    }

    value_priority_map = {
        "ប្រាក់ខែ": "High Salary",
        "ការរីកចម្រើន": "Career Growth",
        "តុល្យភាពការងារនិងជីវិត": "Work-Life Balance",
        "ស្ថិរភាព": "Stability",
        "ឥទ្ធិពលសង្គម": "Social Impact",
    }

    social_preference_map = {
        "ចូលចិត្តខ្លាំង": "Highly Social",
        "មធ្យម": "Moderately Social",
        "មិនចូលចិត្ត": "Less Social",
    }

    future_aspiration_map = {
        "អ្នកជំនាញ": "Expert/Specialist",
        "អ្នកគ្រប់គ្រង": "Manager/Leader",
        "ម្ចាស់អាជីវកម្ម": "Business Owner/Entrepreneur",
        "អ្នកធ្វើការឯករាជ្យ": "Freelancer",
    }

    stress_tolerance_map = {
        "ល្អណាស់": "High",
        "មធ្យម": "Medium",
        "មិនល្អ": "Low",
    }

    location_map = {
        "ភ្នំពេញ": "Phnom Penh",
        "សៀមរាប": "Siem Reap",
        "បាត់ដំបង": "Battambang",
        "កំពង់ចាម": "Kampong Cham",
        "ខេត្តផ្សេងៗ": "Other Provinces",
    }

    gpa_map = {
        "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F"
    }

    budget_map = {
        "$0-$500": "$0-$500",
        "$500-$1000": "$500-$1000",
        "$1000-$2000": "$1000-$2000",
        "លើសពី $2000": "Above $2000",
    }

    english_proficiency_map = {
        "ល្អណាស់": "Excellent",
        "មធ្យម": "Medium",
        "ខ្សោយ": "Poor",
    }

    # Subject and Job Interest mappings (simplified, assuming direct mapping for now)
    # These might need more complex logic if the quiz provides very generic terms
    fav_subjects_map = {
        "គណិតវិទ្យា": "Mathematics",
        "វិទ្យាសាស្ត្រ": "Science",
        "ភាសា": "Language",
        "សង្គម": "Social Studies",
        "សិល្បៈ": "Arts",
    }

    job_interest_map = {
        "អ្នកបង្កើតកម្មវិធី": "Software Developer",
        "វិស្វករ": "Engineer",
        "អ្នកជំនួញ": "Businessman/woman",
        "គ្រូពេទ្យ": "Doctor",
        "គ្រូបង្រៀន": "Teacher",
        "អ្នកទីផ្សារ": "Marketer",
        "សិល្បករ": "Artist",
        "អ្នកគ្រប់គ្រង": "Manager",
    }

    # Apply mappings
    profile = {
        "study_format": study_format_map.get(quiz_ans.get("study_format", ""), quiz_ans.get("study_format")),
        "study_hours": quiz_ans.get("study_hours"), # Assuming numerical or range, no direct mapping needed
        "fav_subjects": [fav_subjects_map.get(s, s) for s in quiz_ans.get("fav_subjects", [])],
        "job_interest": [job_interest_map.get(j, j) for j in quiz_ans.get("job_interest", [])],
        "work_style": work_style_map.get(quiz_ans.get("work_style", ""), quiz_ans.get("work_style")),
        "company_type": company_type_map.get(quiz_ans.get("company_type", ""), quiz_ans.get("company_type")),
        "value_priority": value_priority_map.get(quiz_ans.get("value_priority", ""), quiz_ans.get("value_priority")),
        "social_preference": social_preference_map.get(quiz_ans.get("social_preference", ""), quiz_ans.get("social_preference")),
        "future_aspiration": future_aspiration_map.get(quiz_ans.get("future_aspiration", ""), quiz_ans.get("future_aspiration")),
        "stress_tolerance": stress_tolerance_map.get(quiz_ans.get("stress_tolerance", ""), quiz_ans.get("stress_tolerance")),
        "location": location_map.get(quiz_ans.get("location", ""), quiz_ans.get("location")),
        "gpa": gpa_map.get(quiz_ans.get("gpa", ""), quiz_ans.get("gpa")),
        "budget": budget_map.get(quiz_ans.get("budget", ""), quiz_ans.get("budget")),
        "english_proficiency": english_proficiency_map.get(quiz_ans.get("english_proficiency", ""), quiz_ans.get("english_proficiency"))
    }
    return profile


if __name__ == "__main__":
    main()

# --- END OF DEFINITIVE BUILD --- 