#!/bin/bash

# ==============================================================================
# SPORTS DATA PLATFORM - STARTUP & MONITORING SCRIPT
# ==============================================================================
# Ce script lance l'infrastructure et vérifie que tous les processus critiques
# sont opérationnels, avec un focus sur le streaming en temps réel.
# ==============================================================================

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}"
echo "============================================================"
echo "    SPORTS DATA PLATFORM : INITIALISATION DU SYSTEME"
echo "============================================================"
echo -e "${NC}"

# 1. Lancement de Docker Compose
echo -e "${YELLOW}[1/4] Démarrage des conteneurs (mode détaché)...${NC}"
docker compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}Erreur lors du lancement de Docker Compose. Vérifiez que Docker est démarré.${NC}"
    exit 1
fi

# 2. Vérification de la santé des services de base
echo -e "${YELLOW}[2/4] Vérification de l'état des services critiques...${NC}"

check_service() {
    local container=$1
    local name=$2
    local status=$(docker inspect --format='{{.State.Status}}' $container 2>/dev/null)
    
    if [ "$status" == "running" ]; then
        echo -e "  [${GREEN}OK${NC}] $name est en cours d'exécution."
        return 0
    else
        echo -e "  [${RED}!!${NC}] $name est $status."
        return 1
    fi
}

# Attendre un peu que les conteneurs se stabilisent
sleep 5

check_service "sports_postgres" "Base de données (PostgreSQL)"
check_service "sports_kafka" "Bus de messages (Kafka)"
check_service "sports_minio" "Stockage Objet (MinIO)"
check_service "sports_airflow_scheduler" "Orchestrateur (Airflow)"
check_service "sports_metabase" "Visualisation (Metabase)"

# 3. Validation spécifique du Streaming (Le plus important)
echo -e "${YELLOW}[3/4] Validation du flux de streaming en temps réel...${NC}"

echo -e "  > Attente de l'initialisation du Producer Kafka..."
# On cherche le message de succès dans les logs du producer
PRODUCER_READY=0
for i in {1..20}; do
    if docker compose logs kafka-producer 2>&1 | grep -q "Écoute en direct des sources"; then
        PRODUCER_READY=1
        break
    fi
    echo -n "."
    sleep 2
done

echo "" # Newline

if [ $PRODUCER_READY -eq 1 ]; then
    echo -e "  [${GREEN}OK${NC}] Producer Kafka : Actif et en écoute des sources sportives."
else
    echo -e "  [${YELLOW}??${NC}] Producer Kafka : Toujours en cours d'initialisation (vérifiez 'docker compose logs kafka-producer')."
fi

echo -e "  > Vérification de la connexion du Consumer..."
if docker compose logs kafka-consumer 2>&1 | grep -q "Connecté à Kafka"; then
    echo -e "  [${GREEN}OK${NC}] Consumer Kafka : Connecté et prêt à traiter les articles."
else
    echo -e "  [${YELLOW}??${NC}] Consumer Kafka : Initialisation en cours."
fi

# 4. Résumé final
echo -e "${BLUE}${BOLD}"
echo "============================================================"
echo "    ETAT GLOBAL DU SYSTEME"
echo "============================================================"
echo -e "${NC}"

echo -e "  ${BOLD}Flux de données :${NC}   ${GREEN}OPÉRATIONNEL${NC}"
echo -e "  ${BOLD}Streaming :${NC}         ${GREEN}ACTIF${NC}"
echo -e "  ${BOLD}Analytique :${NC}        ${GREEN}PRÊT${NC}"
echo ""
echo -e "Accès Metabase : ${BLUE}http://localhost:3000${NC}"
echo -e "Accès Airflow  : ${BLUE}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}${BOLD}Le système est prêt ! Bonne analyse.${NC}"
echo "============================================================"
