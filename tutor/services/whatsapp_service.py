import logging

logger = logging.getLogger(__name__)

class WhatsAppReportService:
    @staticmethod
    def send_whatsapp_summary(whatsapp_number, child_name, completion_pct, study_time_mins, hw_status, reading_score, speaking_score, next_goal):
        if not whatsapp_number:
            return {'success': False, 'error': 'WhatsApp number missing'}

        msg = (
            f"🌟 *EduVerse Daily Learning Digest for {child_name}* 🌟\n\n"
            f"✅ *Goal Completion*: {completion_pct}%\n"
            f"⏱️ *Study Time*: {study_time_mins} minutes\n"
            f"📝 *Homework*: {hw_status}\n"
            f"📖 *Reading Score*: {reading_score}%\n"
            f"🗣️ *Speaking Score*: {speaking_score}%\n\n"
            f"🎯 *Tomorrow's Goal*: {next_goal}\n"
            f"Keep up the brilliant work! 🚀"
        )

        logger.info(f"Sending WhatsApp digest to {whatsapp_number}:\n{msg}")

        return {
            'success': True,
            'channel': 'whatsapp',
            'recipient': whatsapp_number,
            'body': msg
        }
