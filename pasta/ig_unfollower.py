#!/usr/bin/env python3
"""
Instagram Unfollower Tool v1.0
==========================================
Baseado na biblioteca instagrapi (API privada oficial do Instagram)

Instalação:
  pip install instagrapi requests

Comandos:
  python3 ig_unfollower.py add             - Adicionar nova conta (login interativo)
  python3 ig_unfollower.py list            - Listar contas salvas
  python3 ig_unfollower.py unfollow        - Iniciar processo de deixar de seguir
  python3 ig_unfollower.py whitelist_add   - Adicionar perfil à lista de exceção
  python3 ig_unfollower.py whitelist_remove- Remover perfil da lista de exceção
  python3 ig_unfollower.py whitelist_list - Listar perfis na lista de exceção
  python3 ig_unfollower.py proxy           - Configurar proxies
  python3 ig_unfollower.py remove          - Remover conta
"""

import sys
import json
import os
import time
import random
import re
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import getpass

# Tentar importar instagrapi
try:
    from instagrapi import Client
    from instagrapi.exceptions import (
        LoginRequired,
        FeedbackRequired,
        PleaseWaitFewMinutes,
        BadPassword,
        ChallengeRequired,
        TwoFactorRequired,
        ReloginAttemptExceeded,
        RateLimitError,
    )

    INSTAGRAPI_AVAILABLE = True

except Exception as e:
    print(f"Erro ao importar instagrapi: {e}")
    INSTAGRAPI_AVAILABLE = False

# ============================================================
# CONFIGURAÇÕES
# ============================================================
CONFIG_FILE = "ig_unfollower_config.json"

# ============================================================
# CLASSE PRINCIPAL
# ============================================================

class InstagramUnfollower:
    def __init__(self):
        self.config = self._load_config()
    
    # ---------- PERSISTÊNCIA ----------
    
    def _load_config(self) -> dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                if "accounts" not in data: data["accounts"] = []
                if "proxies" not in data: data["proxies"] = []
                if "whitelist" not in data: data["whitelist"] = []
                if "settings" not in data:
                    data["settings"] = {
                        "unfollow_delay": 3, # seconds
                        "batch_size": 50,
                        "batch_wait_min": 300, # seconds (5 minutes)
                        "batch_wait_max": 600  # seconds (10 minutes)
                    }
                return data
            except Exception as e:
                print(f"[!] Erro ao ler config: {e}")
        return {
            "accounts": [],
            "proxies": [],
            "whitelist": [],
            "settings": {
                "unfollow_delay": 3,
                "batch_size": 50,
                "batch_wait_min": 300,
                "batch_wait_max": 600
            }
        }
    
    def _save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"[+] Configuração salva em {CONFIG_FILE}")
        except Exception as e:
            print(f"[!] Erro ao salvar config: {e}")
    
    # ---------- PROXIES ----------
    
    def configure_proxies(self):
        print("\n=== CONFIGURAR PROXIES ===")
        print("Formatos aceitos:")
        print("  http://ip:porta")
        print("  http://usuario:senha@ip:porta")
        print("  socks5://ip:porta")
        print("  socks5://usuario:senha@ip:porta")
        print("\nDigite um proxy por linha. Linha vazia para finalizar.\n")
        
        novos = []
        while True:
            linha = input("Proxy > ").strip()
            if not linha:
                break
            if re.match(r'^(https?|socks4|socks5)://', linha):
                novos.append(linha)
                print(f"  [+] Adicionado: {linha[:50]}...")
            else:
                print(f"  [-] Formato inválido: {linha}")
        
        if novos:
            self.config["proxies"] = novos
            self._save_config()
            print(f"[+] {len(novos)} proxies configurados!")
        else:
            print("[-] Nenhum proxy adicionado.")
    
    # ---------- GERENCIAMENTO DE CONTAS ----------
    
    def add_account_interactive(self, username=None, password=None):
        """Adiciona conta via login interativo usando instagrapi."""
        if not INSTAGRAPI_AVAILABLE:
            print("\n[!] Biblioteca instagrapi não encontrada!")
            print("    Instale com: pip install instagrapi")
            return
        
        print("\n" + "=" * 50)
        print("   ADICIONAR NOVA CONTA")
        print("=" * 50)
        
        if username and password:
            metodo = "1"
        else:
            # Escolher método de login
            print("\nMétodo de login:")
            print("  1. Usuário e senha (login direto)")
            print("  2. Session ID (cookie do navegador - recomendado)")
            metodo = input("\nEscolha (1 ou 2): ").strip()
        
        if metodo == "2":
            # Login por sessionid
            sessionid = input("Session ID (copie do cookie do navegador): ").strip()
            if not sessionid:
                print("[-] Session ID inválido.")
                return
            
            username = input("Username da conta: ").strip()
            if not username:
                username = "desconhecido"
            
            print("\n[*] Testando session ID...")
            
            cl = Client()
            
            # Configurar proxy se disponível
            proxy_idx = self._escolher_proxy()
            if proxy_idx is not None:
                proxy_url = self.config["proxies"][proxy_idx]
                cl.set_proxy(proxy_url)
                print(f"  [*] Usando proxy: {proxy_url[:50]}...")
            
            try:
                cl.login_by_sessionid(sessionid)
                
                # Salvar settings para reuso
                settings_file = f"session_{username}.json"
                cl.dump_settings(settings_file)
                
                user_id = cl.user_id
                
                conta = {
                    "username": username,
                    "sessionid": sessionid,
                    "settings_file": settings_file,
                    "user_id": str(user_id),
                    "proxy_idx": proxy_idx,
                    "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid": True,
                    "login_method": "sessionid"
                }
                
                # Verificar se já existe
                for i, c in enumerate(self.config["accounts"]):
                    if c["username"] == username:
                        self.config["accounts"][i] = conta
                        self._save_config()
                        print(f"\n[+] Conta '{username}' atualizada com sucesso!")
                        return
                
                self.config["accounts"].append(conta)
                self._save_config()
                print(f"\n[+] Conta '{username}' adicionada com sucesso!")
                print(f"    User ID: {user_id}")                
            except Exception as e:
                print(f"\n[-] Falha ao usar session ID: {e}")
                print("    Dica: Vá no Instagram.com, faça login, F12 > Application > Cookies > sessionid")
        
        elif metodo == "1":
            # Login por usuário e senha
            if not username:
                username = input("Username/Email: ").strip()
            if not password:
                password = getpass.getpass("Senha: ").strip()
            
            if not username or not password:
                print("[-] Credenciais inválidas.")
                return
            
            print("\n[*] Fazendo login no Instagram (pode levar alguns segundos)...")
            
            cl = Client()
            
            # Configurar delay para simular humano
            cl.delay_range = [1, 3]
            
            # Configurar proxy se disponível
            proxy_idx = self._escolher_proxy()
            if proxy_idx is not None:
                proxy_url = self.config["proxies"][proxy_idx]
                cl.set_proxy(proxy_url)
                print(f"  [*] Usando proxy: {proxy_url[:50]}...")

            try:
                cl.login(username, password)

                # Salvar settings para reuso
                settings_file = f"session_{username}.json"
                cl.dump_settings(settings_file)

                user_id = cl.user_id

                sessionid = ""

                try:
                    cookies = cl.private.cookies
                    if "sessionid" in cookies:
                        sessionid = cookies["sessionid"]
                except Exception:
                    pass

                conta = {
                    "username": username,
                    "password": password,
                    "sessionid": sessionid or "",
                    "settings_file": settings_file,
                    "user_id": str(user_id),
                    "proxy_idx": proxy_idx,
                    "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid": True,
                    "login_method": "password"
                }

                # Verificar se já existe
                for i, c in enumerate(self.config["accounts"]):
                    if c["username"] == username:
                        self.config["accounts"][i] = conta
                        self._save_config()
                        print(f"\n[+] Conta '{username}' atualizada com sucesso!")
                        return

                self.config["accounts"].append(conta)
                self._save_config()

                print(f"\n[+] Conta '{username}' adicionada com sucesso!")
                print(f"    User ID: {user_id}")

            except BadPassword:
                print("\n[-] Senha incorreta para esta conta.")

            except ChallengeRequired:
                print("\n[-] Desafio de segurança requerido!")

            except TwoFactorRequired:
                print("\n[-] Autenticação de dois fatores (2FA) ativada.")

            except FeedbackRequired:
                print("\n[-] Feedback required - Instagram bloqueou temporariamente.")

            except PleaseWaitFewMinutes:
                print("\n[-] Instagram pediu para aguardar.")

            except Exception as e:
                print(f"\n[-] Erro no login: {e}")            
                print("    Dica: Tente usar Session ID (método 2) ao invés de senha.")
        else:
            print("[-] Opção inválida.")
    
    def _escolher_proxy(self) -> Optional[int]:
        """Pergunta se quer usar proxy e retorna o índice."""
        if not self.config.get("proxies"):
            return None
        
        print("\nProxies disponíveis:")
        for i, p in enumerate(self.config["proxies"]):
            print(f"  {i+1}. {p[:60]}...")
        print("  0. Nenhum (sem proxy)")
        
        try:
            escolha = int(input("\nProxy para esta conta (número): ").strip())
            if 1 <= escolha <= len(self.config["proxies"]):
                return escolha - 1
        except:
            pass
        return None
    
    def list_accounts(self):
        accounts = self.config.get("accounts", [])
        if not accounts:
            print("\n[-] Nenhuma conta salva.")
            print("    Use: python3 ig_unfollower.py add")
            return
        
        print("\n=== CONTAS SALVAS ===")
        print(f"{'#':<4} {'Username':<25} {'Status':<10} {'Método':<12} {'Adicionada em':<20}")
        print("-" * 80)
        
        for i, acc in enumerate(accounts):
            username = acc.get("username", "?")
            valid = "✅" if acc.get("valid", True) else "❌"
            metodo = acc.get("login_method", "?")
            added_at = acc.get("added_at", "?")
            print(f"{i+1:<4} {username:<25} {valid:<10} {metodo:<12} {added_at:<20}")
    
    def remove_account(self):
        accounts = self.config.get("accounts", [])
        if not accounts:
            print("\n[-] Nenhuma conta para remover.")
            return
        
        self.list_accounts()
        print("\n0. Voltar")
        
        try:
            escolha = int(input("\nNúmero da conta para remover: ").strip())
            if escolha == 0:
                return
            if 1 <= escolha <= len(accounts):
                removida = accounts.pop(escolha - 1)
                
                # Remover arquivo de sessão também
                settings_file = removida.get("settings_file")
                if settings_file and os.path.exists(settings_file):
                    os.remove(settings_file)
                    print(f"  [*] Arquivo de sessão removido: {settings_file}")
                
                self._save_config()
                print(f"[+] Conta '{removida['username']}' removida com sucesso!")
            else:
                print("[-] Número inválido.")
        except:
            print("[-] Entrada inválida.")
    
    def _get_client_for_account(self, account: dict) -> Optional[Client]:
        cl = Client()
        
        # Configurar proxy
        proxy_idx = account.get("proxy_idx")
        if proxy_idx is not None and proxy_idx < len(self.config.get("proxies", [])):
            cl.set_proxy(self.config["proxies"][proxy_idx])
        
        # Tentar carregar sessão salva
        settings_file = account.get("settings_file")
        if settings_file and os.path.exists(settings_file):
            try:
                cl.load_settings(settings_file)
                cl.private.logger.disabled = True # Desabilitar logs excessivos
                cl.get_timeline_feed()
                return cl
            except (LoginRequired, FeedbackRequired, ReloginAttemptExceeded, BadPassword):
                print(f"  [!] Sessão expirada ou inválida para {account['username']}. Tentando novo login...")
                account["valid"] = False
                self._save_config()
            except Exception as e:
                print(f"  [!] Erro ao carregar sessão para {account['username']}: {e}")
                account["valid"] = False
                self._save_config()
        
        # Se falhou ou não tinha sessão, tentar login com credenciais
        if account.get("login_method") == "password" and account.get("username") and account.get("password"):
            try:
                cl.login(account["username"], account["password"])
                cl.dump_settings(settings_file) # Salvar nova sessão
                account["valid"] = True
                self._save_config()
                return cl
            except Exception as e:
                print(f"  [!] Falha ao fazer login para {account['username']}: {e}")
                account["valid"] = False
                self._save_config()
        elif account.get("login_method") == "sessionid" and account.get("sessionid"):
            try:
                cl.login_by_sessionid(account["sessionid"])
                cl.dump_settings(settings_file) # Salvar nova sessão
                account["valid"] = True
                self._save_config()
                return cl
            except Exception as e:
                print(f"  [!] Falha ao fazer login por sessionid para {account['username']}: {e}")
                account["valid"] = False
                self._save_config()
        
        return None

    # ---------- WHITELIST ----------

    def add_to_whitelist(self, username: str):
        username = username.lower().replace('@', '')
        if username not in self.config["whitelist"]:
            self.config["whitelist"].append(username)
            self._save_config()
            print(f"[+] '{username}' adicionado à lista de exceção.")
        else:
            print(f"[-] '{username}' já está na lista de exceção.")

    def remove_from_whitelist(self, username: str):
        username = username.lower().replace('@', '')
        if username in self.config["whitelist"]:
            self.config["whitelist"].remove(username)
            self._save_config()
            print(f"[+] '{username}' removido da lista de exceção.")
        else:
            print(f"[-] '{username}' não encontrado na lista de exceção.")

    def list_whitelist(self):
        if not self.config["whitelist"]:
            print("\n[-] A lista de exceção está vazia.")
            return
        print("\n=== LISTA DE EXCEÇÃO ===")
        for i, user in enumerate(self.config["whitelist"]):
            print(f"  {i+1}. {user}")

    # ---------- UNFOLLOW ----------

    def unfollow_campaign(self):
        if not INSTAGRAPI_AVAILABLE:
            print("\n[!] instagrapi não instalado. Instale com: pip install instagrapi")
            return
        
        accounts = self.config.get("accounts", [])
        valid_accounts = [a for a in accounts if a.get("valid", True)]
        
        if not valid_accounts:
            print("\n[-] Nenhuma conta válida. Adicione contas primeiro!")
            print("    Use: python3 ig_unfollower.py add")
            return
        
        print("\n" + "=" * 50)
        print("   CAMPANHA DE DEIXAR DE SEGUIR")
        print("=" * 50)
        print(f"Contas disponíveis: {len(valid_accounts)}")
        print(f"Perfis na lista de exceção: {len(self.config['whitelist'])}")

        # Escolher conta para usar
        print("\nEscolha a conta para usar na campanha:")
        for i, acc in enumerate(valid_accounts):
            print(f"  {i+1}. {acc['username']}")
        try:
            escolha = int(input("\nNúmero da conta: ").strip())
            if 1 <= escolha <= len(valid_accounts):
                selected_account = valid_accounts[escolha - 1]
            else:
                print("[-] Escolha inválida.")
                return
        except ValueError:
            print("[-] Entrada inválida.")
            return

        cl = self._get_client_for_account(selected_account)
        if not cl:
            print("[-] Falha ao autenticar a conta selecionada.")
            return

        print(f"[*] Usando a conta: {selected_account['username']}")

        # Obter lista de quem a conta segue
        print("[*] Obtendo lista de perfis que você segue...")
        try:
            # CORREÇÃO AQUI: user_following retorna um dicionário {id: UserShort}
            following_users = cl.user_following(cl.user_id)
            print(f"[+] Você segue {len(following_users)} perfis.")
        except Exception as e:
            print(f"[-] Erro ao obter lista de quem você segue: {e}")
            return

        unfollow_candidates = []
        # CORREÇÃO AQUI: Iterar sobre os valores do dicionário (objetos UserShort)
        for user_id, user_info in following_users.items():
            username = user_info.username.lower()
            if username not in self.config["whitelist"]:
                unfollow_candidates.append(user_info)
            else:
                print(f"[*] Pulando '{username}' (na lista de exceção).")
        
        if not unfollow_candidates:
            print("\n[!] Não há perfis para deixar de seguir (todos na lista de exceção ou você não segue ninguém).")
            return

        print(f"[+] {len(unfollow_candidates)} perfis elegíveis para deixar de seguir.")
        confirm = input("Deseja iniciar a campanha de unfollow? (s/n): ").strip().lower()
        if confirm != 's':
            print("[-] Campanha cancelada.")
            return

        unfollow_delay = self.config["settings"]["unfollow_delay"]
        batch_size = self.config["settings"]["batch_size"]
        batch_wait_min = self.config["settings"]["batch_wait_min"]
        batch_wait_max = self.config["settings"]["batch_wait_max"]

        unfollowed_count = 0
        batch_count = 0

        for i, user_to_unfollow in enumerate(unfollow_candidates):
            username = user_to_unfollow.username
            user_id = user_to_unfollow.pk

            print(f"[*] Deixando de seguir '{username}' ({i+1}/{len(unfollow_candidates)})... ", end="")
            sys.stdout.flush()

            try:
                cl.user_unfollow(user_id)
                print("✅ SUCESSO")
                unfollowed_count += 1
                batch_count += 1
            except RateLimitError:
                wait_time = random.randint(batch_wait_min * 2, batch_wait_max * 2) # Longer wait for rate limit
                print(f"❌ RATE LIMITED! Aguardando {wait_time} segundos antes de tentar novamente...")
                time.sleep(wait_time)
                # Tentar unfollow novamente após a espera
                try:
                    cl.user_unfollow(user_id)
                    print("✅ SUCESSO (após rate limit)")
                    unfollowed_count += 1
                    batch_count += 1
                except Exception as e:
                    print(f"❌ FALHA (após rate limit): {e}")
            except Exception as e:
                print(f"❌ FALHA: {e}")
            
            time.sleep(unfollow_delay)

            if batch_count >= batch_size:
                wait_time = random.randint(batch_wait_min, batch_wait_max)
                print(f"\n[!] Lote de {batch_size} perfis concluído. Aguardando {wait_time} segundos para evitar bloqueio...")
                time.sleep(wait_time)
                batch_count = 0
        
        print("\n" + "=" * 50)
        print("   CAMPANHA DE UNFOLLOW CONCLUÍDA")
        print("=" * 50)
        print(f"[+] Total de perfis deixados de seguir: {unfollowed_count}")


# ============================================================
# CLI
# ============================================================

def print_banner():
    print("""
╔══════════════════════════════════════════╗
║     Instagram Unfollower Tool v1.0       ║
║     Baseado em instagrapi API            ║
╚══════════════════════════════════════════╝
    """)

def main():
    if not INSTAGRAPI_AVAILABLE:
        print("\n[!] Biblioteca necessária: instagrapi")
        print("    Instale com: pip install instagrapi")
        print("    Ou: python3 -m pip install instagrapi\n")
        sys.exit(1)
    
    unfollower = InstagramUnfollower()
    
    if len(sys.argv) < 2:
        print_banner()
        print("Comandos:")
        print("  python3 ig_unfollower.py add             - Adicionar conta (login interativo)")
        print("  python3 ig_unfollower.py list            - Listar contas salvas")
        print("  python3 ig_unfollower.py unfollow        - Iniciar processo de deixar de seguir")
        print("  python3 ig_unfollower.py whitelist_add   - Adicionar perfil à lista de exceção")
        print("  python3 ig_unfollower.py whitelist_remove- Remover perfil da lista de exceção")
        print("  python3 ig_unfollower.py whitelist_list - Listar perfis na lista de exceção")
        print("  python3 ig_unfollower.py proxy           - Configurar proxies")
        print("  python3 ig_unfollower.py remove          - Remover conta")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        unfollower.add_account_interactive()
    elif cmd == "list":
        unfollower.list_accounts()
    elif cmd == "remove":
        unfollower.remove_account()
    elif cmd == "proxy":
        unfollower.configure_proxies()
    elif cmd == "whitelist_add":
        if len(sys.argv) < 3:
            username = input("Digite o @username para adicionar à lista de exceção: ").strip()
            if username: unfollower.add_to_whitelist(username)
        else:
            unfollower.add_to_whitelist(sys.argv[2])
    elif cmd == "whitelist_remove":
        if len(sys.argv) < 3:
            username = input("Digite o @username para remover da lista de exceção: ").strip()
            if username: unfollower.remove_from_whitelist(username)
        else:
            unfollower.remove_from_whitelist(sys.argv[2])
    elif cmd == "whitelist_list":
        unfollower.list_whitelist()
    elif cmd == "unfollow":
        unfollower.unfollow_campaign()
    else:
        print(f"[-] Comando desconhecido: {cmd}")
        print("    Use 'python3 ig_unfollower.py' para ver os comandos disponíveis.")

if __name__ == "__main__":
    main()
