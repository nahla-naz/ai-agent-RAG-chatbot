from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from chatbot.Agent_resp import Chatbot_fns
from chatbot.Reports import ReportUpdater


class chat_view(View):
    def get(self, request):
        return render(request, 'chatbot/chat.html')


@method_decorator(csrf_exempt, name='dispatch')
class chat_response(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.chatbot_fns = Chatbot_fns()
        self.report_updater = ReportUpdater()

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        req_type = data.get("type", "chat")
        print("Request type:", req_type)

        if req_type == "feedback":
            return self.handle_feedback(data)
        else:
            return self.handle_chat(data)

    def handle_chat(self, data):
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "No message provided"}, status=400)

        bot_reply = self.chatbot_fns.get_response(user_message)
        return JsonResponse({"reply": bot_reply})

    def handle_feedback(self, data):
        print("Feedback input received!")

        response_text = data.get("response", "").strip()
        feedback_type = data.get("feedback", "").strip()

        if not response_text or not feedback_type:
            return JsonResponse({"error": "Missing feedback data"}, status=400)

        success = self.report_updater.update_feedback(response_text, feedback_type)

        if success:
            return JsonResponse({"message": "Feedback saved successfully."})
        else:
            return JsonResponse({"message": "No matching response found."})
