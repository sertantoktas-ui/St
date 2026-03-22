#!/usr/bin/env python3
"""
NotebookLM ile Claude API Entegrasyonu

NotebookLM'deki notları Claude API kullanarak:
- Özetleme
- Anahtar noktaları çıkarma
- Soru-Cevap oluşturma
- Ders notları hazırlama
"""

import os
import json
import requests
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# .env dosyasından yükle
load_dotenv()

# İstemci başlat
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# NotebookLM Entegrasyon Araçları
NOTEBOOKLM_TOOLS = [
    {
        "name": "summarize_notes",
        "description": "NotebookLM notlarını özet yaparak önemli noktaları çıkartır",
        "input_schema": {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "string",
                    "description": "Özet yapılacak notlar"
                },
                "summary_length": {
                    "type": "string",
                    "enum": ["short", "medium", "long"],
                    "description": "Özet uzunluğu"
                },
                "language": {
                    "type": "string",
                    "enum": ["tr", "en"],
                    "description": "Özet dili"
                }
            },
            "required": ["notes", "summary_length"]
        }
    },
    {
        "name": "extract_key_points",
        "description": "Notlardan ana noktaları ve kavramları çıkartır",
        "input_schema": {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "string",
                    "description": "Analiz edilecek notlar"
                },
                "max_points": {
                    "type": "integer",
                    "description": "Çıkartılacak maksimum nokta sayısı"
                }
            },
            "required": ["notes"]
        }
    },
    {
        "name": "generate_qa",
        "description": "Notlara dayalı soru-cevap seti oluşturur",
        "input_schema": {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "string",
                    "description": "Sorular oluşturulacak notlar"
                },
                "question_count": {
                    "type": "integer",
                    "description": "Oluşturulacak soru sayısı"
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Soru zorluk seviyesi"
                }
            },
            "required": ["notes", "question_count"]
        }
    },
    {
        "name": "create_study_guide",
        "description": "Notlardan detaylı ders notları ve çalışma rehberi oluşturur",
        "input_schema": {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "string",
                    "description": "Ders notları oluşturulacak içerik"
                },
                "format": {
                    "type": "string",
                    "enum": ["structured", "mindmap", "timeline"],
                    "description": "Çalışma rehberi formatı"
                }
            },
            "required": ["notes", "format"]
        }
    }
]


def summarize_notes(notes: str, summary_length: str = "medium", language: str = "tr") -> str:
    """Notları özetler"""
    length_map = {
        "short": "3-4 cümle",
        "medium": "1 paragraf",
        "long": "2-3 paragraf"
    }

    prompt = f"""
    Aşağıdaki notları {length_map.get(summary_length, '1 paragraf')} ile özet yap.
    Dil: {'Türkçe' if language == 'tr' else 'İngilizce'}

    Notlar:
    {notes}

    Özet:
    """

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text


def extract_key_points(notes: str, max_points: int = 5) -> list:
    """Ana noktaları çıkartır"""
    prompt = f"""
    Aşağıdaki notlardan {max_points} tane ana noktayı ve kavramı çıkart.
    Her bir noktayı kısa ve net bir şekilde ifade et.

    Notlar:
    {notes}

    Ana Noktalar (JSON formatında):
    """

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        result_text = response.content[0].text
        # JSON'u ayıkla
        import re
        json_match = re.search(r'\[.*?\]', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return [point.strip() for point in result_text.split('\n') if point.strip()]
    except:
        return [response.content[0].text]


def generate_qa(notes: str, question_count: int = 5, difficulty: str = "medium") -> dict:
    """Soru-cevap seti oluşturur"""
    difficulty_map = {
        "easy": "basit ve temel",
        "medium": "orta seviye",
        "hard": "zor ve derinlemesine"
    }

    prompt = f"""
    Aşağıdaki notlara dayalı {question_count} tane soru oluştur.
    Zorluk seviyesi: {difficulty_map.get(difficulty, 'orta seviye')}

    Her soru için doğru cevabı da yaz.

    Notlar:
    {notes}

    Soru-Cevap (JSON formatında):
    [
        {{"question": "...", "answer": "..."}},
        ...
    ]
    """

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        result_text = response.content[0].text
        import re
        json_match = re.search(r'\[.*?\]', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"text": response.content[0].text}
    except:
        return {"text": response.content[0].text}


def create_study_guide(notes: str, format: str = "structured") -> str:
    """Çalışma rehberi oluşturur"""
    format_desc = {
        "structured": "başlıklar, alt başlıklar ve madde işaretleriyle yapılandırılmış",
        "mindmap": "merkezi konsept etrafında ağaç yapısında",
        "timeline": "kronolojik sıraya göre zaman çizelgesi şeklinde"
    }

    prompt = f"""
    Aşağıdaki notlardan detaylı bir ders notları ve çalışma rehberi oluştur.
    Format: {format_desc.get(format, 'yapılandırılmış')}

    Rehber şunları içermelidir:
    - Ana konseptler
    - Tanımlar ve açıklamalar
    - Önemli örnekler
    - Özet noktalar

    Notlar:
    {notes}

    Çalışma Rehberi:
    """

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Tool çağrılarını işler"""
    if tool_name == "summarize_notes":
        return summarize_notes(
            tool_input.get("notes", ""),
            tool_input.get("summary_length", "medium"),
            tool_input.get("language", "tr")
        )
    elif tool_name == "extract_key_points":
        points = extract_key_points(
            tool_input.get("notes", ""),
            tool_input.get("max_points", 5)
        )
        return json.dumps({"points": points}, ensure_ascii=False, indent=2)
    elif tool_name == "generate_qa":
        qa = generate_qa(
            tool_input.get("notes", ""),
            tool_input.get("question_count", 5),
            tool_input.get("difficulty", "medium")
        )
        return json.dumps(qa, ensure_ascii=False, indent=2)
    elif tool_name == "create_study_guide":
        return create_study_guide(
            tool_input.get("notes", ""),
            tool_input.get("format", "structured")
        )
    return "Bilinmeyen araç"


def interactive_notebooklm_session():
    """NotebookLM ile etkileşimli oturum başlatır"""
    print("\n" + "="*60)
    print("NotebookLM - Claude API Entegrasyonu")
    print("="*60)
    print("\nNotebookLM notlarınızı Claude AI ile işleyin!")
    print("\nKomutlar:")
    print("- /özetlet: Notları özetle")
    print("- /noktalar: Ana noktaları çıkart")
    print("- /sorular: Soru-cevap oluştur")
    print("- /rehber: Çalışma rehberi oluştur")
    print("- /çıkış: Oturumu sonlandır")
    print("="*60 + "\n")

    messages = []

    while True:
        user_input = input("\nSiz: ").strip()

        if user_input.lower() == "/çıkış":
            print("\nOturum sonlandırıldı. Hoşça kalın!")
            break

        if not user_input:
            continue

        # Kullanıcı mesajını ekle
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Claude'a sor
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            tools=NOTEBOOKLM_TOOLS,
            messages=messages
        )

        # Yanıtı işle
        assistant_message = {"role": "assistant", "content": response.content}
        messages.append(assistant_message)

        # Tool kullanımı kontrol et
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    print(f"\n🔧 Araç kullanılıyor: {tool_name}")
                    tool_result = process_tool_call(tool_name, tool_input)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result
                    })
                elif block.type == "text":
                    print(f"\nClaude: {block.text}")

            # Tool sonuçlarıyla devam et
            if tool_results:
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                final_response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=2000,
                    messages=messages
                )

                for block in final_response.content:
                    if block.type == "text":
                        print(f"\nClaude: {block.text}")

                messages.append({
                    "role": "assistant",
                    "content": final_response.content
                })
        else:
            # Normal yanıt
            for block in response.content:
                if block.type == "text":
                    print(f"\nClaude: {block.text}")


def process_notebook_content(content: str, operation: str = "summarize"):
    """Doğrudan NotebookLM içeriğini işler"""
    operations = {
        "summarize": lambda: summarize_notes(content),
        "extract": lambda: extract_key_points(content),
        "qa": lambda: generate_qa(content, 5),
        "study": lambda: create_study_guide(content)
    }

    if operation in operations:
        return operations[operation]()
    return "Bilinmeyen işlem"


if __name__ == "__main__":
    # Örnek kullanım
    sample_notes = """
    Yapay Zeka ve Makine Öğrenmesi

    Yapay Zeka (AI), bilgisayarların insan zekasını taklit etme yeteneğidir.
    Makine Öğrenmesi (ML), yazılı olarak program yazmak yerine veri kullanarak
    sistemlerin öğrenebilmesini sağlar.

    Temel Konseptler:
    - Veri (Data): Bilgisayarın öğrendiği malzeme
    - Algoritma: Veriden öğrenme prosesi
    - Model: Öğrenilmiş yapı
    - Tahmin: Modelin yeni veriye uygulanması

    Makine Öğrenmesi Türleri:
    1. Denetimli Öğrenme: Etiketlenmiş verilerle öğrenme
    2. Denetimsiz Öğrenme: Örüntü bulma
    3. Güçlendirmeli Öğrenme: Ödül sistem üzerinden öğrenme
    """

    # İnteraktif oturum başlat
    interactive_notebooklm_session()
