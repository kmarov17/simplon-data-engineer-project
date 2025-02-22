## Projet : Analyse des Ventes d'une PME

### Contexte
Ce projet a été réalisé dans le cadre de la préparation à la journée de sélection pour le parcours de formation **Data Engineer** chez Simplon. Il s'agit d'analyser les ventes d'une PME de services numériques sur 30 jours à partir de données fournies (produits, magasins, ventes), en mettant en place une architecture conteneurisée avec Docker, une base de données SQLite, et des analyses SQL.

### Objectifs
1. Concevoir une architecture avec deux services :
   - **Service d'exécution des scripts** (`script-runner`) : Importe les données et effectue les analyses.
   - **Service de stockage** (`data-storage`) : Héberge la base de données SQLite.
2. Explorer et qualifier les données fournies.
3. Créer une base de données cohérente et importer les données.
4. Réaliser des analyses SQL (chiffre d'affaires total, ventes par produit, ventes par région).
5. Stocker les résultats et générer une fiche synthèse.

### Structure du projet

/simplon-data-engineer-project
├── Dockerfile              # Configuration de l'image pour script-runner
├── docker-compose.yml      # Orchestration des services Docker
├── main.py               # Script Python pour l'import, l'analyse et la synthèse
├── products.csv            # Données des produits
├── stores.csv             # Données des magasins
├── sales.csv              # Données des ventes
├── README.md              # Ce fichier


### Prérequis
- **Docker** : Installé et configuré sur votre machine.
- **Docker Compose** : Version compatible avec le fichier `docker-compose.yml`.
- Accès aux fichiers CSV (`products.csv`, `stores.csv`, `sales.csv`) dans le dossier projet.

### Installation et exécution
1. **Cloner ou placer les fichiers dans un dossier** :
   Assurez-vous que tous les fichiers listés dans la structure sont présents dans le répertoire du projet.

2. **Construire et lancer les conteneurs** :
   Dans un terminal, depuis le dossier du projet, exécutez :
   ```
   docker-compose up -d --build
   ```
   - Le service `script-runner` construit l'image à partir du `Dockerfile`, importe les données, crée la base de données, effectue les analyses, et génère `summary.txt`.
   - Le service `data-storage` reste actif pour héberger la base de données dans le volume partagé.

3. **Vérifier les logs** :
   Les logs de `script-runner` indiquent si l'importation et les analyses ont réussi (ex. \Base de données créée, données importées...\).

4. **Arrêter les conteneurs** (facultatif) :
   ```
   docker-compose down
   ```

### Vérification des résultats
- **Accéder à la base de données** :
  Si `data-storage` est actif :
  ```
  docker exec -it simplon-data-engineer-project-data-storage-1 sh
  sqlite3 /data/database.db
  ```
  Commandes utiles :
  ```
  .tables
  SELECT * FROM sales LIMIT 5;
  SELECT * FROM analysis_results;
  ```

- **Récupérer la fiche synthèse** :
  ```
  docker cp simplon-data-engineer-project-data-storage-1:/data/summary.txt ./summary.txt
  ```
  Ouvre `summary.txt` pour voir les résultats (ex. chiffre d'affaires total, ventes par produit/région).

### Livrables
- **Schéma de l'architecture** : Décrit dans ce README (2 services : `script-runner` et `data-storage`, liés par un volume partagé).
- **Schéma de la base de données** : Tables créées dans `main.py` :
  - `products` (product_ref, name, price, stock)
  - `stores` (store_id, city, employees)
  - `sales` (sale_id, date, product_ref, quantity, store_id)
  - `analysis_results` (result_id, analysis_type, result_value, timestamp)
- **Dockerfile** : Fourni dans le dossier.
- **docker-compose.yml** : Fourni dans le dossier.
- **Script d'exécution** : `main.py`.
- **Fiche synthèse** : `summary.txt` généré dans `/data/`.
- **Vidéo de démonstration** : À enregistrer séparément (base vide → exécution → base remplie).

### Résultats attendus
Le fichier `summary.txt` contient :
1. **Chiffre d'affaires total** : Somme de `quantity * price` pour toutes les ventes.
2. **Ventes par produit** : Quantité totale vendue par produit.
3. **Ventes par région** : Chiffre d'affaires par ville.


### Notes
- Les données ne sont importées qu’une fois grâce à une vérification des doublons dans `sales`.
- Le volume `data-volume` persiste entre les exécutions ; pour repartir de zéro, supprimez-le avec :
  ```
  docker volume rm simplon-data-engineer-project-data-volume
  ```

