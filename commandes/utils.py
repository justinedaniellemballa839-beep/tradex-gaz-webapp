from math import radians, sin, cos, sqrt, atan2

FRAIS_MIN = 1000
FRAIS_MAX = 2500
TARIF_PAR_KM = 100


def distance_km(lat1, lng1, lat2, lng2):
    """Distance à vol d'oiseau entre deux points GPS, en kilomètres (formule Haversine)."""
    rayon_terre = 6371
    dlat = radians(float(lat2) - float(lat1))
    dlng = radians(float(lng2) - float(lng1))
    a = sin(dlat / 2) ** 2 + cos(radians(float(lat1))) * cos(radians(float(lat2))) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return rayon_terre * c


def calculer_frais_livraison(lat_client, lng_client, point_distribution):
    """
    Frais de livraison proportionnels à la distance, entre 1000 et 2500 FCFA.
    Si le point de distribution ou la position du client sont indisponibles,
    on applique le minimum.
    """
    if not point_distribution or not point_distribution.latitude or not point_distribution.longitude:
        return FRAIS_MIN
    if not lat_client or not lng_client:
        return FRAIS_MIN

    d = distance_km(lat_client, lng_client, point_distribution.latitude, point_distribution.longitude)
    frais = FRAIS_MIN + d * TARIF_PAR_KM
    return min(max(frais, FRAIS_MIN), FRAIS_MAX)
