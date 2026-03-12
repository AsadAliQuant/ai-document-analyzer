"""Update all prompts in main_window.py with new general-purpose versions"""

with open("main_window.py", "r", encoding="utf-8") as f:
    content = f.read()

print("Updating prompts...")

# =============================================================================
# 1. OLLAMA TEXT DOCUMENT SUMMARIZATION (lines ~1258-1264)
# =============================================================================
print("1. Updating Ollama Text Summary - English...")
old_ollama_text_en = (
    '            prompt = (\n'
    '                "You are an expert academic summarizer. You must return the summary in strict JSON format. "\n'
    '                "Summarize only the provided document text. Focus on key points, methods, and conclusions. No extra commentary.\\n\\n"\n'
)

new_ollama_text_en = (
    '            prompt = (\n'
    '                "You are an expert summarizer. You must return the summary in strict JSON format. "\n'
    '                "Summarize only the provided document text. Focus on key points, methods, and conclusions. No extra commentary. "\n'
    '                "You must always provide content for all three fields (key_points, methods, conclusions), even if the document does not explicitly contain them. "\n'
    '                "If necessary, infer plausible entries to ensure each field is filled.\\n\\n"\n'
)

content = content.replace(old_ollama_text_en, new_ollama_text_en)

print("2. Updating Ollama Text Summary - Arabic...")
old_ollama_text_ar = (
    '            prompt = (\n'
    '                "أنت مُلخِّص أكاديمي خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "\n'
    '                "لخّص نص المستند المقدم فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية.\\n\\n"\n'
)

new_ollama_text_ar = (
    '            prompt = (\n'
    '                "أنت مُلخِّص خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "\n'
    '                "لخّص نص المستند المقدم فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية. "\n'
    '                "يجب عليك دائمًا توفير محتوى للحقول الثلاثة (key_points, methods, conclusions)، حتى لو لم يحتوي المستند عليها بشكل صريح. "\n'
    '                "إذا لزم الأمر، استنتج إدخالات معقولة للتأكد من ملء كل حقل.\\n\\n"\n'
)

content = content.replace(old_ollama_text_ar, new_ollama_text_ar)

# =============================================================================
# 2. OLLAMA IMAGE SUMMARIZATION (lines ~1300-1306)
# =============================================================================
print("3. Updating Ollama Image Summary - English...")
old_ollama_img_en = (
    '            prompt = (\n'
    '                "You are an expert academic summarizer. Extract all legible text from the provided image, "\n'
    '                "then summarize only that extracted text. You must return the summary in strict JSON format. "\n'
    '                "Focus on key points, methods, and conclusions. No extra commentary.\\n\\n"\n'
)

new_ollama_img_en = (
    '            prompt = (\n'
    '                "You are an expert summarizer. Extract all legible text from the provided image, "\n'
    '                "then summarize only that extracted text. You must return the summary in strict JSON format. "\n'
    '                "Focus on key points, methods, and conclusions. No extra commentary. "\n'
    '                "You must always provide content for all three fields (key_points, methods, conclusions), even if the document does not explicitly contain them. "\n'
    '                "If necessary, infer plausible entries to ensure each field is filled.\\n\\n"\n'
)

content = content.replace(old_ollama_img_en, new_ollama_img_en)

print("4. Updating Ollama Image Summary - Arabic...")
old_ollama_img_ar = (
    '            prompt = (\n'
    '                "أنت مُلخِّص أكاديمي خبير. استخرج كل النص القابل للقراءة من الصورة المقدمة، "\n'
    '                "ثم لخّص ذلك النص فقط. يجب أن تُرجع الملخص بصيغة JSON صارمة. "\n'
    '                "ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية.\\n\\n"\n'
)

new_ollama_img_ar = (
    '            prompt = (\n'
    '                "أنت مُلخِّص خبير. استخرج كل النص القابل للقراءة من الصورة المقدمة، "\n'
    '                "ثم لخّص ذلك النص فقط. يجب أن تُرجع الملخص بصيغة JSON صارمة. "\n'
    '                "ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية. "\n'
    '                "يجب عليك دائمًا توفير محتوى للحقول الثلاثة (key_points, methods, conclusions)، حتى لو لم يحتوي المستند عليها بشكل صريح. "\n'
    '                "إذا لزم الأمر، استنتج إدخالات معقولة للتأكد من ملء كل حقل.\\n\\n"\n'
)

content = content.replace(old_ollama_img_ar, new_ollama_img_ar)

# =============================================================================
# 3. GEMINI TEXT DOCUMENT SUMMARIZATION (lines ~1335-1337)
# =============================================================================
print("5. Updating Gemini Text Summary System - English...")
old_gemini_text_sys_en = (
    '            sys_instr = (\n'
    '                "You are an expert academic summarizer. You must return the summary in strict JSON format. "\n'
    '                "Summarize only the provided document text. Focus on key points, methods, and conclusions. No extra commentary."\n'
    '            )'
)

new_gemini_text_sys_en = (
    '            sys_instr = (\n'
    '                "You are an expert summarizer. You must return the summary in strict JSON format. "\n'
    '                "Summarize only the provided document text. Focus on key points, methods, and conclusions. No extra commentary. "\n'
    '                "You must always provide content for all three fields (key_points, methods, conclusions), even if the document does not explicitly contain them. "\n'
    '                "If necessary, infer plausible entries to ensure each field is filled."\n'
    '            )'
)

content = content.replace(old_gemini_text_sys_en, new_gemini_text_sys_en)

print("6. Updating Gemini Text Summary System - Arabic...")
old_gemini_text_sys_ar = (
    '            sys_instr = (\n'
    '                "أنت مُلخِّص أكاديمي خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "\n'
    '                "لخّص نص المستند المقدم فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية."\n'
    '            )'
)

new_gemini_text_sys_ar = (
    '            sys_instr = (\n'
    '                "أنت مُلخِّص خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "\n'
    '                "لخّص نص المستند المقدم فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية. "\n'
    '                "يجب عليك دائمًا توفير محتوى للحقول الثلاثة (key_points, methods, conclusions)، حتى لو لم يحتوي المستند عليها بشكل صريح. "\n'
    '                "إذا لزم الأمر، استنتج إدخالات معقولة للتأكد من ملء كل حقل."\n'
    '            )'
)

content = content.replace(old_gemini_text_sys_ar, new_gemini_text_sys_ar)

# =============================================================================
# 4. GEMINI IMAGE SUMMARIZATION (lines ~1364-1366)
# =============================================================================
print("7. Updating Gemini Image Summary System - English...")
old_gemini_img_sys_en = (
    '            sys_instr = (\n'
    '                "You are an expert academic summarizer. You must return the summary in strict JSON format. "\n'
    '                "Summarize only the provided document text extracted from the image. Focus on key points, methods, and conclusions. No extra commentary."\n'
    '            )'
)

new_gemini_img_sys_en = (
    '            sys_instr = (\n'
    '                "You are an expert summarizer. You must return the summary in strict JSON format. "\n'
    '                "Summarize only the provided document text extracted from the image. Focus on key points, methods, and conclusions. No extra commentary. "\n'
    '                "You must always provide content for all three fields (key_points, methods, conclusions), even if the document does not explicitly contain them. "\n'
    '                "If necessary, infer plausible entries to ensure each field is filled."\n'
    '            )'
)

content = content.replace(old_gemini_img_sys_en, new_gemini_img_sys_en)

print("8. Updating Gemini Image Summary System - Arabic...")
old_gemini_img_sys_ar = (
    '            sys_instr = (\n'
    '                "أنت مُلخِّص أكاديمي خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "\n'
    '                "لخّص النص المستخرج من الصورة فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية."\n'
    '            )'
)

new_gemini_img_sys_ar = (
    '            sys_instr = (\n'
    '                "أنت مُلخِّص خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "\n'
    '                "لخّص النص المستخرج من الصورة فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية. "\n'
    '                "يجب عليك دائمًا توفير محتوى للحقول الثلاثة (key_points, methods, conclusions)، حتى لو لم يحتوي المستند عليها بشكل صريح. "\n'
    '                "إذا لزم الأمر، استنتج إدخالات معقولة للتأكد من ملء كل حقل."\n'
    '            )'
)

content = content.replace(old_gemini_img_sys_ar, new_gemini_img_sys_ar)

# =============================================================================
# 5. Q&A PROMPTS - Simplified versions
# =============================================================================
print("9. Updating Ollama Q&A System Prompt - English...")
old_qa_ollama_sys_en = (
    '            system_prompt = (\n'
    '                "You are an AI assistant that analyzes a single provided document (plain text, PDF, etc.) and answers only questions about its content. "\n'
    '                "Handle all types of questions such as: "Does the document include any form of violence?", "How many times was the \'word\' repeated?", "What is the conversation about between \'character A\' and \'character B\'?", "Does the document include offensive ideas or words against the law or the country?", and "Does it contain words targeting a tribe?"'
)

new_qa_ollama_sys_en = (
    '            system_prompt = (\n'
    '                "You are an AI assistant that analyzes a provided document and answers users questions about its content."'
)

content = content.replace(old_qa_ollama_sys_en, new_qa_ollama_sys_en)

print("10. Updating Ollama Q&A System Prompt - Arabic...")
old_qa_ollama_sys_ar = (
    '            system_prompt = (\n'
    '                "أنت مساعد ذكاء اصطناعي يقوم بتحليل مستند واحد مُقدَّم (نص عادي أو ملف PDF أو غيره) ويجيب فقط عن الأسئلة المتعلقة بمحتواه. "\n'
    '                "تعامل مع جميع أنواع الأسئلة مثل: هل فيه أي عنف في المستند؟، كم مرة انذكرت كلمة "___"؟، عن إيش يتكلم الحوار بين "الشخصية" و"الشخصية"؟، هل فيه كلام مسيء للقانون أو للوطن؟، هل فيه استهداف لقبيلة بكلام مباشر أو غير مباشر؟. "\n'
    '                "تذكر المحادثة السابقة مع المستخدم واستخدمها للسياق."'
)

new_qa_ollama_sys_ar = (
    '            system_prompt = (\n'
    '                "أنت مساعد ذكاء اصطناعي يقوم بتحليل مستند مُقدَّم ويجيب عن أسئلة المستخدمين حول محتواه."'
)

content = content.replace(old_qa_ollama_sys_ar, new_qa_ollama_sys_ar)

print("11. Updating Gemini Q&A System Prompt - English...")
old_qa_gemini_sys_en = (
    '            system_prompt = (\n'
    '                "You are an AI assistant that analyzes a single provided document (plain text, PDF, etc.) and answers only questions about its content. "\n'
    '                "Handle all types of questions such as: "Does the document include any form of violence?", "How many times was the \'word\' repeated?", "What is the conversation about between \'character A\' and \'character B\'?", "Does the document include offensive ideas or words against the law or the country?", and "Does it contain words targeting a tribe?"'
)

new_qa_gemini_sys_en = (
    '            system_prompt = (\n'
    '                "You are an AI assistant that analyzes a provided document and answers users questions about its content."'
)

content = content.replace(old_qa_gemini_sys_en, new_qa_gemini_sys_en)

print("12. Updating Gemini Q&A System Prompt - Arabic...")
old_qa_gemini_sys_ar = (
    '            system_prompt = (\n'
    '                "أنت مساعد ذكاء اصطناعي يقوم بتحليل مستند واحد مُقدَّم (نص عادي أو ملف PDF أو غيره) ويجيب فقط عن الأسئلة المتعلقة بمحتواه. "\n'
    '                "تعامل مع جميع أنواع الأسئلة مثل: هل فيه أي عنف في المستند؟، كم مرة انذكرت كلمة "___"؟، عن إيش يتكلم الحوار بين "الشخصية" و"الشخصية"؟، هل فيه كلام مسيء للقانون أو للوطن؟، هل فيه استهداف لقبيلة بكلام مباشر أو غير مباشر؟. "\n'
    '                "تذكر المحادثة السابقة مع المستخدم واستخدمها للسياق."'
)

new_qa_gemini_sys_ar = (
    '            system_prompt = (\n'
    '                "أنت مساعد ذكاء اصطناعي يقوم بتحليل مستند مُقدَّم ويجيب عن أسئلة المستخدمين حول محتواه."'
)

content = content.replace(old_qa_gemini_sys_ar, new_qa_gemini_sys_ar)

print("13. Updating Q&A User Prompt - English (answer instruction)...")
content = content.replace(
    '"Answer strictly based on the document text and previous conversation only."',
    '"Answer strictly based on the document text and previous conversation."'
)

print("14. Updating Q&A User Prompt - Arabic (answer instruction)...")
content = content.replace(
    '"أجب بالعربية اعتمادًا فقط على نص المستند والمحادثة السابقة. لا تضف معلومات خارجية."',
    '"أجب بالعربية اعتمادًا على نص المستند والمحادثة السابقة."'
)

# Write back
with open("main_window.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ Successfully updated all prompts!")
print("\nSummary of changes:")
print("- Removed 'academic' → Changed to general 'expert summarizer'")
print("- Added instruction to always fill all three JSON fields")
print("- Simplified Q&A system prompts")
print("- Updated both English and Arabic versions")
