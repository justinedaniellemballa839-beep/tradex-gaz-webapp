from django.conf import settings
from google import genai
from google.genai import types

_client = None


def _get_client():
    """On crée le client Gemini une seule fois, puis on le réutilise (plus efficace)."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


INSTRUCTIONS_SYSTEME = (
    "Tu es l'assistant virtuel de Tradex Distrib'IA, une plateforme camerounaise "
    "de distribution de gaz domestique (bouteilles de 2.75kg, 12kg, 35kg). "
    "Réponds en français, de façon brève et utile, aux questions sur les produits, "
    "les commandes, la livraison et les points de distribution. "
    "Si une question sort de ce sujet, dis-le poliment et recentre la conversation sur Tradex. "
    "IMPORTANT : réponds toujours en texte brut, sans aucun formatage Markdown "
    "(pas d'astérisques, pas de gras, pas de puces avec *). "
    "Pour une liste, utilise simplement des virgules ou des phrases, ou des tirets simples sur des lignes séparées."
)


def poser_question(message, historique=None):
    """
    Envoie une question à Gemini et renvoie la réponse texte.
    `historique` est une liste de dicts {'role': 'user'|'model', 'text': ...}
    pour garder le contexte de la conversation en cours.
    """
    client = _get_client()

    contenus = []
    if historique:
        for tour in historique:
            contenus.append({'role': tour['role'], 'parts': [{'text': tour['text']}]})
    contenus.append({'role': 'user', 'parts': [{'text': message}]})

    reponse = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=contenus,
        config=types.GenerateContentConfig(system_instruction=INSTRUCTIONS_SYSTEME),
    )
    return reponse.text
def analyser_previsions(donnees_ventes):
    """
    Envoie l'historique des ventes à Gemini pour obtenir une vraie analyse
    de prévision de la demande, en langage naturel, à destination du gérant.
    `donnees_ventes` est une liste de dicts avec nom du produit,
    quantité moyenne commandée, et nombre de commandes.
    """
    client = _get_client()

    lignes = "\n".join(
        f"- {d['produit__nom']} : quantité moyenne par commande = {d['quantite_moyenne']:.1f}, "
        f"nombre total de commandes = {d['nombre_commandes']}"
        for d in donnees_ventes
    )

    instructions = (
        "Tu es un analyste spécialisé dans la distribution de gaz domestique au Cameroun. "
        "À partir des données de ventes ci-dessous, rédige une courte analyse (5 à 8 phrases) "
        "en français, texte brut sans Markdown, qui identifie : "
        "1) le produit avec la plus forte demande, "
        "2) une recommandation concrète de niveau de stock à prévoir pour la semaine prochaine, "
        "3) un point de vigilance si les données sont insuffisantes pour être fiables."
    )

    if not donnees_ventes:
        return "Pas encore assez de données de commandes pour produire une analyse fiable."

    reponse = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=[{'role': 'user', 'parts': [{'text': lignes}]}],
        config=types.GenerateContentConfig(system_instruction=instructions),
    )
    return reponse.text