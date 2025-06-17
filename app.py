import json
import os
import time
import subprocess
import sys
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


KEYWORDS = ["hotel", "hotellerie", "restaurant", "casino"]

# --- UTILITAIRES DE SUPPRESSION ET DE TRAITEMENT ---

def clean_json_and_extract(json_path, extract_dir):
    if os.path.exists(json_path):
        print(f"Suppression du fichier JSON : {json_path}")
        os.remove(json_path)
    if os.path.exists(extract_dir):
        folders = [os.path.join(extract_dir, d) for d in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, d))]
        for folder in folders:
            print(f"Suppression du dossier extrait : {folder}")
            shutil.rmtree(folder)

def clean_last_archive(download_dir, extract_dir):
    files = [f for f in os.listdir(download_dir) if f.endswith(".tar.gz")]
    if not files:
        print(f"Aucune archive à supprimer dans {download_dir}")
        return
    files.sort(reverse=True)
    last_file = files[0]
    last_file_path = os.path.join(download_dir, last_file)
    print(f"Suppression de l'archive : {last_file_path}")
    os.remove(last_file_path)
    folder_name = os.path.splitext(os.path.splitext(last_file)[0])[0]
    extracted_folder = os.path.join(extract_dir, folder_name)
    if os.path.isdir(extracted_folder):
        print(f"Suppression du dossier extrait : {extracted_folder}")
        shutil.rmtree(extracted_folder)

def download_archive(fetch_script):
    print(f"Téléchargement de l'archive avec {fetch_script} ...")
    result = subprocess.run([sys.executable, fetch_script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Erreur lors du téléchargement :\n{result.stderr}")

def parse_to_json(parse_script):
    print(f"Parsing et génération du JSON avec {parse_script} ...")
    result = subprocess.run([sys.executable, parse_script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Erreur lors du parsing :\n{result.stderr}")

def refresh_all():
    FILIERES = [
        {
            "name": "LEGI",
            "fetch_script": "code_legi/fetch_only.py",
            "parse_script": "code_legi/parse_only.py",
            "download_dir": "code_legi/legi_download",
            "extract_dir": "code_legi/legi_extract",
            "json_path": "data/articles_legi.json",
        },
        {
            "name": "KALI",
            "fetch_script": "code_kali/fetch_only.py",
            "parse_script": "code_kali/parse_only.py",
            "download_dir": "code_kali/kali_download",
            "extract_dir": "code_kali/kali_extract",
            "json_path": "data/articles_kali.json",
        },
        {
            "name": "CASS",
            "fetch_script": "code_cass/fetch_only.py",
            "parse_script": "code_cass/parse_only.py",
            "download_dir": "code_cass/cass_download",
            "extract_dir": "code_cass/cass_extract",
            "json_path": "data/articles_cass.json",
        },
        {
            "name": "JADE",
            "fetch_script": "code_jade/fetch_only.py",
            "parse_script": "code_jade/parse_only.py",
            "download_dir": "code_jade/jade_download",
            "extract_dir": "code_jade/jade_extract",
            "json_path": "data/articles_jade.json",
        },
        {
            "name": "JORF",
            "fetch_script": "code_jorf/fetch_only.py",
            "parse_script": "code_jorf/parse_only.py",
            "download_dir": "code_jorf/jorf_download",
            "extract_dir": "code_jorf/jorf_extract",
            "json_path": "data/articles_jorf.json",
        },
    ]
    for f in FILIERES:
        print(f"\n=== Rafraîchissement {f['name']} ===")
        clean_json_and_extract(f["json_path"], f["extract_dir"])
        clean_last_archive(f["download_dir"], f["extract_dir"])
        download_archive(f["fetch_script"])
        parse_to_json(f["parse_script"])
        print(f"=== {f['name']} terminé ===")

# --- RECHERCHE ET AFFICHAGE ---



def load_articles(json_path):
    if not os.path.exists(json_path):
        return []
    try:
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []



def filter_articles(articles, keywords):
    filtered = []
    for article in articles:
        texte = (article.get("texte") or "").lower()
        if any(kw in texte for kw in keywords) and article.get("date_fin") == "2999-01-01":
            filtered.append(article)
    return filtered



def print_results(db_name, articles):
    print(f"\n=== {db_name} ===")
    if not articles:
        print("Aucun article trouvé.")
        return
    for article in articles:
        code = article.get("code", "")
        num = article.get("article", "")
        titre = article.get("titre", "")
        print(f"- {code} - Article {num} : {titre}")
    print(f"Total: {len(articles)} article(s) en vigueur trouvés avec les mots-clés.")



def send_email(subject, body, to_email):

    from_email = "yldz.ma60@gmail.com"
    password = "bsid aaid gfak gwpz" 

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        print("Email envoyé avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")


def main():
    refresh_all()
    FILIERES = [
        ("LEGI", "data/articles_legi.json"),
        ("KALI", "data/articles_kali.json"),
        ("CASS", "data/articles_cass.json"),
        ("JADE", "data/articles_jade.json"),
        ("JORF", "data/articles_jorf.json"),
    ]
    all_results = []
    for db_name, path in FILIERES:
        articles = load_articles(path)
        filtered = filter_articles(articles, KEYWORDS)
        print_results(db_name, filtered)
        if filtered:
            all_results.append((db_name, filtered))


    if all_results:       

        # Mets les mots-clés tout en haut du mail
        message = "Mots-clés utilisés pour la recherche : " + ", ".join(KEYWORDS) + "\n\n"
        message += "Bonjour,\n\nVoici les nouveaux articles et lois qui ont été mis à jour :\n\n"
        for db_name, articles in all_results:
            message += f"=== {db_name} ===\n"
            for article in articles:
                code = article.get("code", "")
                num = article.get("article", "")
                titre = article.get("titre") or "(pas de details)"
                message += f"- {code} - Article {num} : {titre}\n"
            message += "\n"
        message += "\nAfin d'avoir davantage d'informations, veuillez vous rendre sur le site suivant : https://u9yssb7ybrkcsvsjupktfy.streamlit.app/\n"
        send_email(
            subject="Nouveaux articles trouvés",
            body=message,
            to_email="yldz.ma60@gmail.com"
        )


import time
import requests
from bs4 import BeautifulSoup
import re


def get_latest_filename(base_url, prefix):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")
    tar_links = sorted(
        [a["href"] for a in soup.find_all("a", href=True) if re.match(rf"{prefix}_.*\.tar\.gz", a["href"])],
        reverse=True
    )
    if not tar_links:
        return None
    return tar_links[0]

def get_local_filename(download_dir):
    files = [f for f in os.listdir(download_dir) if f.endswith(".tar.gz")]
    if not files:
        return None
    files.sort(reverse=True)
    return files[0]


def wait_and_check_new_data():
    legi_download_dir = "code_legi/legi_download"
    kali_download_dir = "code_kali/kali_download"
    while True:
        print("Vérification de la dernière archive LEGI et KALI disponible...")
        latest_legi_online = get_latest_filename("https://echanges.dila.gouv.fr/OPENDATA/LEGI/", "LEGI")
        latest_legi_local = get_local_filename(legi_download_dir)
        latest_kali_online = get_latest_filename("https://echanges.dila.gouv.fr/OPENDATA/KALI/", "KALI")
        latest_kali_local = get_local_filename(kali_download_dir)
        print(f"LEGI en ligne : {latest_legi_online}")
        print(f"LEGI locale : {latest_legi_local}")
        print(f"KALI en ligne : {latest_kali_online}")
        print(f"KALI locale : {latest_kali_local}")

        maj_legi = latest_legi_online and latest_legi_online != latest_legi_local
        maj_kali = latest_kali_online and latest_kali_online != latest_kali_local

        if maj_legi or maj_kali:
            print("Nouvelle archive détectée (LEGI ou KALI), lancement du traitement complet.")
            main()
            print("Traitement terminé. Nouvelle attente de 24h.")
            time.sleep(86400)
        else:
            print("Aucune nouvelle archive. Nouvelle vérification dans 24h.")
            time.sleep(86400)

if __name__ == "__main__":
    wait_and_check_new_data()