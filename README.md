Instagram Unfollower Tool v1.1 🚀

Ferramenta de automação para deixar de seguir perfis no Instagram de forma segura, com sistema de whitelist e proteção anti-ban.

Criado por: @kauan_da_silva_md3


---

📋 Requisitos

No Linux (Ubuntu/Debian/etc)

sudo apt update && sudo apt install python3 python3-pip -y

No Termux (Android)

pkg update && pkg upgrade
pkg install python python-pip git -y


---

⚙️ Instalação do Projeto

1. Clonar o repositório

git clone https://github.com/kauandasilvamd3/instagram-unfollower-bot.git
cd instagram-unfollower-bot


---

2. Instalar dependências (requirements.txt)

pip install -r requirements.txt


---

📥 Instalação Manual (Alternativa)

Baixe:

ig_unfollower.py

requirements.txt


Depois execute:

pip install -r requirements.txt


---

🚀 Como Usar

Adicionar conta

python3 ig_unfollower.py add

Adicionar à whitelist

python3 ig_unfollower.py whitelist_add @usuario

Iniciar unfollow

python3 ig_unfollower.py unfollow


---

📌 Outros Comandos

python3 ig_unfollower.py list
python3 ig_unfollower.py whitelist_list
python3 ig_unfollower.py whitelist_remove @usuario
python3 ig_unfollower.py proxy
python3 ig_unfollower.py remove


---

🛡️ Segurança Anti-Ban

⏱️ Delay de 3 segundos entre ações

⏸️ Pausas automáticas a cada 50 unfollows

🚨 Detecção de bloqueio temporário



---

⚠️ Aviso

Use com responsabilidade. Automação pode violar os termos do Instagram.


---

Créditos: @kauan_da_silva_md3
