# Phantom_opera_AI

## Algorithme

L'algorithme s'applique pour les deux rôles jouables (inspecteur et fantôme).

Il est adapté du Monte-Carlo, et se divise donc en 4 parties (Séléction, Expansion, Simulation et Rétropropagation).

L'algorithme est lancé à chaque séléction de personnage. Lorsque l'algorithme selectionne la première fois un personnage sur un tour, l'algorihme génère les réponses pour deux personnages afin de finir le tour (pour relever des données pour la rétropropagation, voir [Rétropropagation](#Rétropropagation)). Cepandant, afin d'obtenir une plus grande précision et/ou d'avoir plus de temps de simulation sur le second personnage, on relance l'algorithme à la selection de celui-ci.

L'algorithme se lance pendant 7 secondes, afin de laisser une marge de 3 secondes sur le timeout du serveur.

### Sélection
Pour la phase de séléction, nous utilisons la formule UCT (Upper Confidence Bound 1 applied to Trees) pour le compromis entre exploitation et exploration.

### Expansion et Simulation
Afin de créer une simulation, nous avons réutilisé le code du serveur. Nous avons enlevé toute la partie communication et modifier l'initialisation pour permettre de commencer une simulation à n'importe quel tour de la partie.
Chaque simulation se poursuit jusqu'à la fin du tour.

A chaque question posée par la simulation au rôle joué par l'algorithme, on complète ou construit l'arbre avec les réponses envoyées à celle-ci.

Un adversaire génére des réponses réponses aléatoires dans la simulation.
Pour un arbre plus cohérent, il fallait que les questions que pose la simulation à l'algorithme restent les mêmes. Il fallait alors que cet adversaire réponde toujours une même réponse à une même question à la simulation, afin de retrouver la même situation. Ces réponses sont donc sauvegardées (en dehors de l'arbre).

### Rétropropagation
A la fin de chaque simulation, on effectue la mise à jour de l'arbre par la rétropropagation de la donnée de victoire et du nombre de personnages innocentés optimisé pour le rôle joué (voir [Choix des réponses](#Choix-des-réponses)).

La victoire sur un tour est définie comme suit : 
- S'il n'y a eu aucune personne innocentée ou qu'il y en a eu une mais que le fantôme a crié, le fantôme gagne ce tour.
- Dans le cas contraire, c'est l'inspecteur qui gagne ce tour

## Choix des réponses
Une fois l'algorithme terminé, nous choisissons les réponses les plus prometteuses à envoyer au serveur, et on définit le nœud principal de l'arbre sur cette réponse (pour libérer la mémoire le plus vite possible).

Si aucune victoire n'est trouvée, ou que deux choix présentent le même ratio de simulations gagnées/jouées, le choix s'effectuera alors en fonction du nombre d'innocents le plus optimal en fonction du rôle joué.

## To launch a game

1) python3 server.py

2) python3 marius_inspector.py

3) python3 marius_fantom.py

De Valentin Lebon et Marius Michelot


