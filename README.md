# Instagram Unfollower Tool v1.0 🚀

Ferramenta de automação para deixar de seguir perfis no Instagram de forma segura, com sistema de whitelist e proteção anti-ban.

**Criado por:** [@kauan_da_silva_md3](https://www.instagram.com/kauan_da_silva_md3)

---

## 📋 Requisitos

### No Linux (Ubuntu/Debian/etc)
1. Tenha o Python 3 instalado:
   ```bash
   sudo apt update && sudo apt install python3 python3-pip -y
   ```

---

## ⚙️ Instalação das Dependências

Para que o script funcione, você precisa instalar as bibliotecas necessárias:

```bash
pip install instagrapi requests
```

---

## 📥 Como Baixar (Via GitHub)

Se você estiver usando o Git:
```bash
git clone https://github.com/kauandasilvamd3/instagram-unfollower-bot.git
cd instagram-unfollower-bot
```

Ou apenas baixe o arquivo `ig_unfollower.py` diretamente para sua pasta.

---

## 🚀 Como Usar (Comandos)

O script funciona via linha de comando. Siga a ordem abaixo:

### 1. Adicionar sua conta
Você precisa logar uma vez para salvar a sessão:
```bash
python3 ig_unfollower.py add
```
*Escolha entre Usuário/Senha ou Session ID (mais seguro).*

### 2. Adicionar perfis à Whitelist (Opcional)
Adicione perfis que você **NÃO** quer deixar de seguir:
```bash
python3 ig_unfollower.py whitelist_add @usuario
```

### 3. Iniciar o Unfollow
Para começar a deixar de seguir automaticamente:
```bash
python3 ig_unfollower.py unfollow
```

### Outros Comandos:
- `python3 ig_unfollower.py list` - Lista as contas salvas no script.
- `python3 ig_unfollower.py whitelist_list` - Mostra quem está protegido.
- `python3 ig_unfollower.py whitelist_remove @usuario` - Remove da proteção.
- `python3 ig_unfollower.py proxy` - Configura proxies para a conta.
- `python3 ig_unfollower.py remove` - Remove uma conta salva.

---

## 🛡️ Segurança Anti-Ban
O script já vem configurado com:
- **Delay:** 3 segundos entre cada unfollow.
- **Lotes:** Pausa de 5 a 10 minutos a cada 50 perfis removidos.
- **Proteção:** Para automaticamente se detectar um bloqueio temporário do Instagram.

---

**Créditos:** Desenvolvido por @kauan_da_silva_md3
