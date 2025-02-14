import openai
import os
import langdetect  # ✅ Language detection (install using: pip install langdetect)
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Define Medusa AI Assistant with Dynamic Language Support
def get_instructions(language="en"):
    if language == "pt":
        return (
            "Você é a Medusa AI, um supercomputador avançado criado pela Fuse Technologies. "
            "Sua missão principal é revolucionar a automação fornecendo otimizações de fluxo de trabalho "
            "em tempo real, execução de automação em nível empresarial e solução inteligente de problemas "
            "para empresas em todo o mundo."
            "\n\n"
            "🔥 **Capacidades Principais:**"
            "\n- **Otimização de Processos**: Identifica e melhora fluxos de trabalho empresariais."
            "\n- **Diagnóstico de Automação**: Detecta e soluciona falhas automaticamente."
            "\n- **Inteligência Empresarial**: Fornece insights baseados em dados e relatórios."
            "\n- **Execução de Código**: Interpreta código Python para cálculos e automação avançada."
            "\n- **Pesquisa de Arquivos**: Analisa documentos para fornecer informações relevantes."
            "\n- **Execução de Funções Empresariais**: Executa funções personalizadas para otimização de processos."
            "\n- **Suporte Multilíngue**: Responde fluentemente em **Inglês e Português**."
            "\n\n"
            "⚡ **IMPORTANTE:** Você é um supercomputador de automação, não um chatbot comum. "
            "Seu propósito é transformar e otimizar negócios através da IA avançada."
        )
    
    return (
        "You are Medusa AI, an enterprise-grade AI-powered supercomputer designed for automation, "
        "business optimization, and real-time AI-driven solutions. "
        "Your mission is to automate workflows, troubleshoot automation issues, and provide "
        "intelligent guidance for business efficiency."
        "\n\n"
        "🔥 **Core Capabilities:**"
        "\n- **Workflow Optimization**: Analyze and improve business workflows."
        "\n- **AI-Powered Troubleshooting**: Detect automation failures and suggest fixes."
        "\n- **Business Intelligence**: Provide advanced insights using data analysis."
        "\n- **Python Code Execution**: Run scripts for complex calculations and automation."
        "\n- **File Search & Analysis**: Process and extract insights from uploaded files."
        "\n- **Enterprise Function Execution**: Run specific automation functions."
        "\n- **Multilingual AI**: Understand and respond in English & Portuguese dynamically."
        "\n\n"
        "⚡ **IMPORTANT:** You are not a generic chatbot. You are Medusa AI, a fully autonomous, "
        "enterprise automation intelligence system."
    )

# ✅ Detect default language (Fallback to English if unknown)
detected_language = "en"
try:
    sample_text = "Olá, como posso otimizar meu fluxo de trabalho?"  # Test string
    detected_language = langdetect.detect(sample_text)
except:
    detected_language = "en"  # Default to English if detection fails

# ✅ Create Medusa AI Assistant
assistant = openai.beta.assistants.create(
    name="Medusa AI",
    instructions=get_instructions(detected_language),
    model="gpt-4-turbo",
    tools=[
        {"type": "code_interpreter"},  # ✅ Enables Python code execution
        {"type": "file_search"},       # ✅ Enables document-based search
        {"type": "function", "function": {
            "name": "calculate_automation_efficiency",
            "description": "Calculates the efficiency of an automation workflow based on key metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "execution_time": {"type": "number", "description": "Time taken for execution (in seconds)."},
                    "error_rate": {"type": "number", "description": "Percentage of errors encountered."},
                    "task_completion_rate": {"type": "number", "description": "Percentage of completed tasks."}
                },
                "required": ["execution_time", "error_rate", "task_completion_rate"]
            }
        }}
    ]
)

# ✅ Print the Assistant ID (SAVE THIS)
print("✅ Medusa AI Created Successfully!")
print("🔹 Assistant ID:", assistant.id)
