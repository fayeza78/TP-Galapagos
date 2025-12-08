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
  uri: 'http://localhost:4000',
  cache: new InMemoryCache(),
});

// Requêtes GraphQL

const GET_DASHBOARD = gql`
  query GetDashboard {
    hydravions {
      id
      modele
      statut
      consommation
      portActuel {
        nom
        ile
      }
    }
    ports {
      id
      nom
      ile
    }
    dockers {
      id
      disponible
    }
    lockers {
      id
      isAvailable
      capacity
      location
    }
  }
`;

const GET_FORM_DATA = gql`
  query GetFormData {
    clients {
      id
      name
    }
    produits {
      id
      name
      stock
    }
    ports {
      id
      nom
    }
    hydravions {
      id
      modele
      statut
    }
  }
`;

const GET_CLIENTS = gql`
  query GetClients {
    clients {
      id
      name
      type
      email
    }
  }
`;

const GET_SHORTEST_PATH = gql`
  query GetPath($depart: ID!, $arrivee: ID!) {
    shortestPath(depart: $depart, arrivee: $arrivee) {
      distanceKm
      dureeMinutes
      etapes {
        nom
      }
    }
  }
`;

const GET_LOCKERS = gql`
  query GetLockers {
    lockers {
      id
      location
      capacity
      isAvailable
    }
  }
`;

const ADD_COMMANDE = gql`
  mutation AddCommande($clientId: ID!, $products: [ProduitInCommandeInput!]!) {
    addCommande(clientId: $clientId, products: $products) {
      id
    }
  }
`;

const ADD_LIVRAISON = gql`
  mutation AddLivraison(
    $commandeId: ID!
    $hydravionId: ID!
    $depart: String!
    $arrivee: String!
    $dateEstimee: String
  ) {
    addLivraison(
      commandeId: $commandeId
      hydravionId: $hydravionId
      depart: $depart
      arrivee: $arrivee
      dateEstimee: $dateEstimee
    ) {
      id
      statut
      trajet {
        distanceKm
        dureeMinutes
      }
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

  const dockersDispo = data.dockers.filter((d) => d.disponible).length;
  const totalDockers = data.dockers.length;

  const lockersDispo = data.lockers.filter((l) => l.isAvailable).length;
  const totalLockers = data.lockers.length;

  return (
    <div className="dashboard">
      <div className="stats-bar">
        <div className="stat-card">
          <h3>Flotte</h3>
          <p>{data.hydravions.length} avions</p>
        </div>
        <div className="stat-card">
          <h3>Dockers dispo</h3>
          <p>
            {dockersDispo} / {totalDockers}
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
          <p>{data.ports.length} îles</p>
        </div>
      </div>

      <h2>État de la flotte</h2>
      <div className="grid-container">
        {data.hydravions.map((h) => (
          <div
            key={h.id}
            className={`card ${h.statut === 'En Vol' ? 'flying' : 'parked'}`}
          >
            <div className="card-header">
              <span className="icon">
                {h.statut === 'En Vol' ? '✈️' : '⚓'}
              </span>
              <h4>{h.modele}</h4>
            </div>
            <div className="card-body">
              <p>
                <strong>Statut :</strong> {h.statut}
              </p>
              <p>
                <strong>Position :</strong>{' '}
                {h.portActuel ? h.portActuel.nom : 'Maintenance'}
              </p>
              <p>
                <strong>Conso :</strong> {h.consommation} L/100km
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
          clientId: form.clientId,
          products: [
            {
              productId: form.productId,
              quantity: parseInt(form.quantity, 10),
            },
          ],
        },
      });

      const commandeId = cmdRes.data.addCommande.id;

      await createLivraison({
        variables: {
          commandeId,
          hydravionId: form.hydravionId,
          depart: form.depart,
          arrivee: form.arrivee,
          dateEstimee: new Date().toISOString(),
        },
      });

      setSuccessMsg('Livraison planifiée avec succès.');
    } catch (err) {
      console.error(err);
      alert('Erreur pendant la création de la livraison');
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
                {c.name}
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
                {p.name} (Stock : {p.stock})
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
              .filter((h) => h.statut !== 'En Vol')
              .map((h) => (
                <option key={h.id} value={h.id}>
                  {h.modele}
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
                {formData.ports.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nom}
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
                {formData.ports.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nom}
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

          {pathData && pathData.shortestPath && (
            <div className="path-card">
              <h3>Trajet proposé</h3>
              <div className="path-metrics">
                <div>{pathData.shortestPath.distanceKm} km</div>
                <div>{pathData.shortestPath.dureeMinutes} min</div>
              </div>
              <ul className="steps-list">
                {pathData.shortestPath.etapes.map((e, i) => (
                  <li key={i}>{e.nom}</li>
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

  return (
    <div className="lockers-page">
      <h2>Lockers</h2>
      <p>Disponibilité des différents lockers.</p>

      <div className="lockers-list">
        {lockers.map((l) => (
          <div
            key={l.id}
            className={'locker-card' + (l.isAvailable ? ' available' : ' busy')}
          >
            <h3>Locker #{l.id}</h3>
            <p>Lieu : {l.location}</p>
            <p>Capacité : {l.capacity}</p>
            <p>Statut : {l.isAvailable ? 'Disponible' : 'Occupé'}</p>
          </div>
        ))}
      </div>
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
              <h3>{c.name}</h3>
              <p>ID : {c.id}</p>
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
              <h3>{selectedClient.name}</h3>
              <p>ID : {selectedClient.id}</p>
              <p>Métier : {selectedClient.type}</p>
              <p>Email : {selectedClient.email}</p>
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
