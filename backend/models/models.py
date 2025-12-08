from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


# ========== Modèles MongoDB ==========

class HydravionModele(str, Enum):
    """Différents modèles d'hydravions avec leurs caractéristiques"""
    PETIT = "petit"  # 50 caisses, 15L/100km
    MOYEN = "moyen"  # 100 caisses, 20L/100km
    GRAND = "grand"  # 150 caisses, 25L/100km


class StatutHydravion(str, Enum):
    """États possibles d'un hydravion"""
    ENTREPOT = "entrepot"
    PORT = "port"
    EN_VOL = "en_vol"
    MAINTENANCE = "maintenance"


class Coordonnees(BaseModel):
    """Coordonnées GPS d'un lieu"""
    latitude: float
    longitude: float


class Hydravion(BaseModel):
    """Modèle d'un hydravion"""
    nom: str
    modele: HydravionModele
    capacite_caisses: int  # Entre 50 et 150
    consommation_carburant: float  # Litres par 100km
    statut: StatutHydravion
    position: Optional[Coordonnees] = None
    port_actuel: Optional[str] = None
    carburant_actuel: Optional[float] = 100.0  # Pourcentage


class RoleClient(str, Enum):
    """Types de clients scientifiques"""
    VOLCANOLOGUE = "volcanologue"
    BIOLOGISTE_MARIN = "biologiste_marin"
    ZOOLOGUE = "zoologue"
    BOTANISTE = "botaniste"
    GEOLOGUE = "geologue"


class Client(BaseModel):
    """Modèle d'un client scientifique"""
    nom: str
    prenom: str
    email: str
    telephone: str
    role: RoleClient
    organisation: str
    ile_principale: str  # Île où le client travaille principalement


class CategorieProduit(str, Enum):
    """Catégories de matériel scientifique"""
    EQUIPEMENT_PLONGEE = "equipement_plongee"
    MATERIEL_LABORATOIRE = "materiel_laboratoire"
    EQUIPEMENT_OBSERVATION = "equipement_observation"
    MATERIEL_CAMPING = "materiel_camping"
    ECHANTILLONS = "echantillons"
    MEDICAMENTS = "medicaments"


class Produit(BaseModel):
    """Modèle d'un produit scientifique"""
    nom: str
    description: str
    categorie: CategorieProduit
    poids: float  # En kg
    dimensions: Dict[str, float]  # hauteur, largeur, profondeur en cm
    stock_disponible: int


class StatutCommande(str, Enum):
    """États d'une commande"""
    EN_ATTENTE = "en_attente"
    EN_PREPARATION = "en_preparation"
    PRETE = "prete"
    EN_LIVRAISON = "en_livraison"
    LIVREE = "livree"
    ANNULEE = "annulee"


class Commande(BaseModel):
    """Modèle d'une commande client"""
    client_id: str
    produits: List[Dict[str, any]]  # [{"produit_id": "xxx", "quantite": 2}]
    port_destination: str
    nombre_caisses_requises: int
    date_commande: datetime
    date_livraison_souhaitee: Optional[datetime] = None
    statut: StatutCommande
    priorite: int = 1  # 1-5, 5 étant le plus prioritaire


class Stock(BaseModel):
    """Modèle de gestion du stock"""
    produit_id: str
    quantite_disponible: int
    quantite_reservee: int
    seuil_alerte: int
    derniere_mise_a_jour: datetime


class StatutLocker(str, Enum):
    """État d'un locker"""
    VIDE = "vide"
    PLEIN = "plein"
    RESERVE = "reserve"


class Locker(BaseModel):
    """Modèle d'un locker de stockage sur une île"""
    numero: int
    ile: str
    port: str
    taille_caisse: int  # Capacité en nombre de caisses (toujours 1)
    statut: StatutLocker
    commande_id: Optional[str] = None
    date_remplissage: Optional[datetime] = None


class Livraison(BaseModel):
    """Modèle d'une livraison"""
    commande_id: str
    hydravion_id: str
    itineraire: List[str]  # Liste des ports dans l'ordre
    caisses_livrees: int
    distance_totale: float  # En km
    consommation_estimee: float  # En litres
    date_depart: datetime
    date_arrivee_estimee: datetime
    date_arrivee_reelle: Optional[datetime] = None
    statut: str


# ========== Modèles pour Neo4J ==========

class IleNode(BaseModel):
    """Modèle d'une île (nœud Neo4J)"""
    nom: str
    coordonnees: Coordonnees
    superficie: float  # En km²
    population: Optional[int] = 0
    description: str


class PortNode(BaseModel):
    """Modèle d'un port (nœud Neo4J)"""
    nom: str
    ile: str
    coordonnees: Coordonnees
    nombre_lockers: int
    capacite_hydravions: int


class RouteRelation(BaseModel):
    """Modèle d'une route entre deux ports (relation Neo4J)"""
    port_depart: str
    port_arrivee: str
    distance: float  # En km (ligne droite)
    temps_vol_estime: float  # En minutes


# ========== Modèles pour GraphQL ==========

class HydravionInput(BaseModel):
    """Input pour créer/modifier un hydravion"""
    nom: str
    modele: str
    statut: str
    port_actuel: Optional[str] = None


class CommandeInput(BaseModel):
    """Input pour créer une commande"""
    client_id: str
    produits: List[Dict[str, any]]
    port_destination: str
    date_livraison_souhaitee: Optional[str] = None
    priorite: Optional[int] = 1
