import React, { useState } from 'react';
import {
  ApolloClient,
  InMemoryCache,
  ApolloProvider,
  useQuery,
  useLazyQuery,
  useMutation,
  gql,
} from '@apollo/client';
import './App.css';

// Config Apollo (backend en local)
const client = new ApolloClient({
  uri: 'http://localhost:8000/graphql',
  cache: new InMemoryCache(),
});

// Requêtes GraphQL

const GET_DASHBOARD = gql`
  query GetDashboard {
    hydravions {
      id
      nom
      modele
      statut
      consommation_carburant
      port_actuel
      carburant_actuel
      capacite_caisses
    }
    ports {
      nom
      ile
      nombre_lockers
      capacite_hydravions
    }
    lockers {
      id
      numero
      statut
      port
      ile
      taille_caisse
    }
  }
`;

const GET_FORM_DATA = gql`
  query GetFormData {
    clients {
      id
      nom
      prenom
      email
      role
      organisation
      ile_principale
    }
    produits {
      id
      nom
      description
      categorie
      stock_disponible
      poids
    }
    ports {
      nom
      ile
      capacite_hydravions
    }
    hydravions {
      id
      nom
      modele
      statut
      capacite_caisses
    }
  }
`;

const GET_CLIENTS = gql`
  query GetClients {
    clients {
      id
      nom
      prenom
      email
      role
      organisation
      ile_principale
    }
  }
`;

const GET_SHORTEST_PATH = gql`
  query GetPath($depart: String!, $arrivee: String!) {
    routeOptimale(port_depart: $depart, port_arrivee: $arrivee) {
      distance_totale
      temps_total_estime
      ports
    }
  }
`;

const GET_LOCKERS = gql`
  query GetLockers {
    lockers {
      id
      numero
      statut
      port
      ile
      taille_caisse
    }
  }
`;

const ADD_COMMANDE = gql`
  mutation CreerCommande(
    $client_id: String!
    $produits: [ProduitCommandeInput!]!
    $port_destination: String!
    $priorite: Int
  ) {
    creerCommande(
      input: {
        client_id: $client_id
        produits: $produits
        port_destination: $port_destination
        priorite: $priorite
      }
    ) {
      id
      statut
      nombre_caisses_requises
    }
  }
`;

const ADD_LIVRAISON = gql`
  mutation CreerLivraison(
    $commande_id: String!
    $hydravion_id: String!
    $itineraire: [String!]!
  ) {
    creerLivraison(
      commande_id: $commande_id
      hydravion_id: $hydravion_id
      itineraire: $itineraire
    ) {
      id
      statut
      distance_totale
      consommation_estimee
    }
  }
`;

// DASHBOARD
function Dashboard() {
  const { loading, error, data } = useQuery(GET_DASHBOARD);

  if (loading) {
    return <p>Chargement du dashboard...</p>;
  }

  if (error) {
    return <p>Erreur : {error.message}</p>;
  }

  const lockersDispo = data.lockers.filter((l) => l.statut === 'vide').length;
  const totalLockers = data.lockers.length;

  const hydravionsDispo = data.hydravions.filter(
    (h) => h.statut === 'entrepot' || h.statut === 'port'
  ).length;

  return (
    <div className="dashboard">
      <div className="stats-bar">
        <div className="stat-card">
          <h3>Flotte</h3>
          <p>
            {hydravionsDispo} / {data.hydravions.length} disponibles
          </p>
        </div>
        <div className="stat-card">
          <h3>Lockers dispo</h3>
          <p>
            {lockersDispo} / {totalLockers}
          </p>
        </div>
        <div className="stat-card">
          <h3>Ports desservis</h3>
          <p>{data.ports.length} ports</p>
        </div>
        <div className="stat-card">
          <h3>Capacité totale</h3>
          <p>
            {data.hydravions.reduce((sum, h) => sum + h.capacite_caisses, 0)}{' '}
            caisses
          </p>
        </div>
      </div>

      <h2>État de la flotte</h2>
      <div className="grid-container">
        {data.hydravions.map((h) => (
          <div
            key={h.id}
            className={`card ${h.statut === 'en_vol' ? 'flying' : 'parked'}`}
          >
            <div className="card-header">
              <span className="icon">
                {h.statut === 'en_vol' ? '✈️' : '⚓'}
              </span>
              <h4>{h.nom || h.modele}</h4>
            </div>
            <div className="card-body">
              <p>
                <strong>Modèle :</strong> {h.modele}
              </p>
              <p>
                <strong>Statut :</strong> {h.statut}
              </p>
              <p>
                <strong>Position :</strong>{' '}
                {h.port_actuel || 'En maintenance'}
              </p>
              <p>
                <strong>Capacité :</strong> {h.capacite_caisses} caisses
              </p>
              <p>
                <strong>Conso :</strong> {h.consommation_carburant} L/100km
              </p>
              <p>
                <strong>Carburant :</strong> {h.carburant_actuel}%
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// NOUVELLE LIVRAISON
function NewDelivery() {
  const { data: formData } = useQuery(GET_FORM_DATA);
  const [calculatePath, { data: pathData, loading: pathLoading }] =
    useLazyQuery(GET_SHORTEST_PATH);

  const [createCommande] = useMutation(ADD_COMMANDE);
  const [createLivraison] = useMutation(ADD_LIVRAISON);

  const [form, setForm] = useState({
    clientId: '',
    productId: '',
    quantity: 1,
    hydravionId: '',
    depart: '',
    arrivee: '',
  });
  const [successMsg, setSuccessMsg] = useState('');

  const handleCalculate = () => {
    if (form.depart && form.arrivee) {
      calculatePath({
        variables: { depart: form.depart, arrivee: form.arrivee },
      });
    }
  };

  const handleSubmit = async () => {
    try {
      const cmdRes = await createCommande({
        variables: {
          client_id: form.clientId,
          produits: [
            {
              produit_id: form.productId,
              quantite: parseInt(form.quantity, 10),
            },
          ],
          port_destination: form.arrivee,
          priorite: 3,
        },
      });

      const commandeId = cmdRes.data.creerCommande.id;

      const itineraire = pathData?.routeOptimale?.ports || [
        form.depart,
        form.arrivee,
      ];

      await createLivraison({
        variables: {
          commande_id: commandeId,
          hydravion_id: form.hydravionId,
          itineraire: itineraire,
        },
      });

      setSuccessMsg('Livraison planifiée avec succès.');
    } catch (err) {
      console.error(err);
      alert('Erreur pendant la création de la livraison: ' + err.message);
    }
  };

  if (!formData) {
    return <p>Chargement du formulaire...</p>;
  }

  return (
    <div className="delivery-panel">
      <h2>Nouvelle expédition</h2>

      <div className="form-grid">
        <div className="form-section">
          <label>Client</label>
          <select
            value={form.clientId}
            onChange={(e) => setForm({ ...form, clientId: e.target.value })}
          >
            <option value="">-- Choisir --</option>
            {formData.clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.prenom} {c.nom} - {c.role}
              </option>
            ))}
          </select>

          <label>Produit</label>
          <select
            value={form.productId}
            onChange={(e) => setForm({ ...form, productId: e.target.value })}
          >
            <option value="">-- Choisir --</option>
            {formData.produits.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nom} (Stock : {p.stock_disponible})
              </option>
            ))}
          </select>

          <label>Quantité</label>
          <input
            type="number"
            min="1"
            value={form.quantity}
            onChange={(e) => setForm({ ...form, quantity: e.target.value })}
          />

          <hr />

          <label>Hydravion</label>
          <select
            value={form.hydravionId}
            onChange={(e) => setForm({ ...form, hydravionId: e.target.value })}
          >
            <option value="">-- Choisir --</option>
            {formData.hydravions
              .filter((h) => h.statut !== 'en_vol' && h.statut !== 'en_maintenance')
              .map((h) => (
                <option key={h.id} value={h.id}>
                  {h.nom} ({h.modele}) - {h.capacite_caisses} caisses
                </option>
              ))}
          </select>

          <div className="route-select">
            <div>
              <label>Départ</label>
              <select
                value={form.depart}
                onChange={(e) => setForm({ ...form, depart: e.target.value })}
              >
                <option value="">-- Port --</option>
                {formData.ports.map((p, i) => (
                  <option key={i} value={p.nom}>
                    {p.nom} ({p.ile})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Arrivée</label>
              <select
                value={form.arrivee}
                onChange={(e) => setForm({ ...form, arrivee: e.target.value })}
              >
                <option value="">-- Port --</option>
                {formData.ports.map((p, i) => (
                  <option key={i} value={p.nom}>
                    {p.nom} ({p.ile})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button className="btn-calc" onClick={handleCalculate}>
            Calculer l&apos;itinéraire
          </button>
        </div>

        <div className="result-section">
          {pathLoading && <p>Calcul du trajet...</p>}

          {pathData && pathData.routeOptimale && (
            <div className="path-card">
              <h3>Trajet proposé</h3>
              <div className="path-metrics">
                <div>{pathData.routeOptimale.distance_totale} km</div>
                <div>{pathData.routeOptimale.temps_total_estime} min</div>
              </div>
              <ul className="steps-list">
                {pathData.routeOptimale.ports.map((portName, i) => (
                  <li key={i}>{portName}</li>
                ))}
              </ul>

              <button className="btn-validate" onClick={handleSubmit}>
                Valider l&apos;expédition
              </button>
            </div>
          )}

          {successMsg && <div className="success-box">{successMsg}</div>}
        </div>
      </div>
    </div>
  );
}

function Lockers() {
  const { loading, error, data } = useQuery(GET_LOCKERS);

  if (loading) {
    return <p>Chargement des lockers...</p>;
  }

  if (error) {
    return <p>Erreur : {error.message}</p>;
  }

  const lockers = data ? data.lockers : [];
  const lockersByPort = {};

  lockers.forEach((l) => {
    if (!lockersByPort[l.port]) {
      lockersByPort[l.port] = [];
    }
    lockersByPort[l.port].push(l);
  });

  return (
    <div className="lockers-page">
      <h2>Lockers</h2>
      <p>Disponibilité des différents lockers par port.</p>

      {Object.entries(lockersByPort).map(([port, portLockers]) => (
        <div key={port} style={{ marginBottom: '30px' }}>
          <h3>{port}</h3>
          <div className="lockers-list">
            {portLockers.map((l) => (
              <div
                key={l.id}
                className={'locker-card' + (l.statut === 'vide' ? ' available' : ' busy')}
              >
                <h4>Locker #{l.numero}</h4>
                <p>Île : {l.ile}</p>
                <p>Taille : {l.taille_caisse}</p>
                <p>
                  Statut :{' '}
                  {l.statut === 'vide'
                    ? 'Disponible'
                    : l.statut === 'plein'
                    ? 'Occupé'
                    : 'Réservé'}
                </p>
              </div>
            ))}
          </div>
        </div>
      ))}

      {lockers.length === 0 && <p>Aucun locker trouvé.</p>}
    </div>
  );
}

function Client() {
  const { loading, error, data } = useQuery(GET_CLIENTS);
  const [selectedClientId, setSelectedClientId] = useState(null);

  if (loading) {
    return <p>Chargement des clients...</p>;
  }

  if (error) {
    return <p>Erreur : {error.message}</p>;
  }

  const clients = data ? data.clients : [];
  const selectedClient = clients.find((c) => c.id === selectedClientId) || null;

  return (
    <div className="clients-page">
      <h2>Clients</h2>

      <div className="clients-layout">
        <div className="clients-list">
          {clients.map((c) => (
            <div
              key={c.id}
              className={
                'client-card' +
                (selectedClientId === c.id ? ' client-card--selected' : '')
              }
              onClick={() => setSelectedClientId(c.id)}
            >
              <h3>
                {c.prenom} {c.nom}
              </h3>
              <p>{c.role}</p>
            </div>
          ))}

          {clients.length === 0 && <p>Aucun client trouvé.</p>}
        </div>

        <div className="client-details">
          {!selectedClient && (
            <p>Sélectionner un client pour voir les détails.</p>
          )}

          {selectedClient && (
            <>
              <h3>
                {selectedClient.prenom} {selectedClient.nom}
              </h3>
              <p>
                <strong>Email :</strong> {selectedClient.email}
              </p>
              <p>
                <strong>Rôle :</strong> {selectedClient.role}
              </p>
              <p>
                <strong>Organisation :</strong> {selectedClient.organisation}
              </p>
              <p>
                <strong>Île principale :</strong> {selectedClient.ile_principale}
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function App() {
  const [view, setView] = useState('dashboard');

  return (
    <ApolloProvider client={client}>
      <div className="App">
        <nav className="sidebar">
          <h1>
            Richnou
            <br />
            Galapagos
          </h1>
          <ul>
            <li
              onClick={() => setView('dashboard')}
              className={view === 'dashboard' ? 'active' : ''}
            >
              Dashboard
            </li>
            <li
              onClick={() => setView('delivery')}
              className={view === 'delivery' ? 'active' : ''}
            >
              Nouvelle livraison
            </li>
            <li
              onClick={() => setView('clients')}
              className={view === 'clients' ? 'active' : ''}
            >
              Clients
            </li>
            <li
              onClick={() => setView('lockers')}
              className={view === 'lockers' ? 'active' : ''}
            >
              Lockers
            </li>
          </ul>
        </nav>

        <main className="main-content">
          {view === 'dashboard' && <Dashboard />}
          {view === 'delivery' && <NewDelivery />}
          {view === 'clients' && <Client />}
          {view === 'lockers' && <Lockers />}
        </main>
      </div>
    </ApolloProvider>
  );
}

export default App;
