import os
import shutil

KEYWORDS = ["hotel", "hotellerie", "restaurant", "casino"]

# Import des fonctions utilitaires
from code_legi.utils import load_articles as load_legi, filter_articles as filter_legi
from code_kali.utils import load_articles as load_kali, filter_articles as filter_kali
from code_cass.utils import load_articles as load_cass, filter_articles as filter_cass
from code_jade.utils import load_articles as load_jade, filter_articles as filter_jade
from code_jorf.utils import load_articles as load_jorf, filter_articles as filter_jorf

def clean_dir(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            print(f"Suppression du fichier : {path}")
            os.remove(path)
        else:
            print(f"Suppression du dossier : {path}")
            shutil.rmtree(path)
    else:
        print(f"Rien à supprimer pour : {path}")

def refresh_filiere(
    filiere,
    fetch_script,
    parse_script,
    download_dir,
    extract_dir,
    json_path
):
    print(f"\n=== Rafraîchissement {filiere} ===")
    # Suppression des anciens fichiers
    clean_dir(download_dir)
    clean_dir(extract_dir)
    clean_dir(json_path)
    # Téléchargement du dernier fichier
    print(f"Téléchargement du dernier fichier pour {filiere}...")
    os.system(f"python {fetch_script}")
    print(f"Téléchargement terminé pour {filiere}.")
    # Extraction et parsing
    print(f"Extraction et parsing pour {filiere}...")
    os.system(f"python {parse_script}")
    print(f"Extraction et parsing terminés pour {filiere}.")

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

def main():
    FILIERES = [
        {
            "name": "LEGI",
            "fetch_script": "code_legi/fetch_only.py",
            "parse_script": "code_legi/parse_only.py",
            "download_dir": "code_legi/legi_download",
            "extract_dir": "code_legi/legi_extract",
            "json_path": "data/articles_legi.json",
            "loader": load_legi,
            "filter": filter_legi,
        },
        {
            "name": "KALI",
            "fetch_script": "code_kali/fetch_only.py",
            "parse_script": "code_kali/parse_only.py",
            "download_dir": "code_kali/kali_download",
            "extract_dir": "code_kali/kali_extract",
            "json_path": "data/articles_kali.json",
            "loader": load_kali,
            "filter": filter_kali,
        },
        {
            "name": "CASS",
            "fetch_script": "code_cass/fetch_only.py",
            "parse_script": "code_cass/parse_only.py",
            "download_dir": "code_cass/cass_download",
            "extract_dir": "code_cass/cass_extract",
            "json_path": "data/articles_cass.json",
            "loader": load_cass,
            "filter": filter_cass,
        },
        {
            "name": "JADE",
            "fetch_script": "code_jade/fetch_only.py",
            "parse_script": "code_jade/parse_only.py",
            "download_dir": "code_jade/jade_download",
            "extract_dir": "code_jade/jade_extract",
            "json_path": "data/articles_jade.json",
            "loader": load_jade,
            "filter": filter_jade,
        },
        {
            "name": "JORF",
            "fetch_script": "code_jorf/fetch_only.py",
            "parse_script": "code_jorf/parse_only.py",
            "download_dir": "code_jorf/jorf_download",
            "extract_dir": "code_jorf/jorf_extract",
            "json_path": "data/articles_jorf.json",
            "loader": load_jorf,
            "filter": filter_jorf,
        },
    ]

    # Rafraîchir toutes les filières
    for f in FILIERES:
        refresh_filiere(
            f["name"],
            f["fetch_script"],
            f["parse_script"],
            f["download_dir"],
            f["extract_dir"],
            f["json_path"]
        )

    # Recherche et affichage
    for f in FILIERES:
        print(f"\nRecherche des articles pour {f['name']}...")
        articles = f["loader"](f["json_path"])
        filtered = [
            a for a in f["filter"](articles, search_all=None)
            if any(kw in (a.get("texte") or "").lower() for kw in KEYWORDS)
            and a.get("date_fin") == "2999-01-01"
        ]
        print_results(f["name"], filtered)

if __name__ == "__main__":
    main()