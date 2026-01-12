# Agarta.io - Multiplayer Agar.io Klon

---

## Slide 1: O Projekte
- **Multiplayer hra** typu Agar.io
- **Python + Pygame** - jednoduchá a rýchla implementácia
- **Sieťová architektúra** - klient-server model
- **Real-time gameplay** - 60 FPS server, interpolácia na klientovi

---

## Slide 2: Hlavné Funkcie
- **Hráči** - pohyb myšou, rast zbieraním jedla
- **Split mechanika** - rozdelenie na menšie bunky (Space)
- **Vírusy** - zelené objekty rozdeľujúce hráčov
- **Scoreboard** - TOP 10 hráčov podľa mass
- **Dynamická kamera** - prispôsobuje sa veľkosti hráča

---

## Slide 3: Sieťová Architektúra
- **TCP komunikácia** - spoľahlivý prenos dát (port 5678)
- **UDP discovery** - automatické vyhľadávanie serverov (port 5679)
- **Broadcast messaging** - server posiela stav všetkým klientom
- **Threading** - paralelné spracovanie pripojení

---

## Slide 4: Optimalizácie
- **Culling** - renderovanie len viditeľných objektov
- **Throttling** - obmedzenie frekvencie správ (60 FPS → 30 FPS state)
- **Cache fontov** - zníženie alokácií pamäte
- **Efektívne collision detection** - rýchle kontroly vzdialenosti

---

## Slide 5: Hostovanie Servera
- **Jednoduché hostovanie** - jedno kliknutie v menu
- **Automatické zobrazenie IP** - pre ľahké pripojenie
- **Čakanie na hráčov** - minimálne 2 hráči na začatie
- **Lokálny aj sieťový režim** - 127.0.0.1 alebo LAN IP

---

## Slide 6: Technické Detaily
- **Server** - game loop, collision detection, state management
- **Klient** - rendering, interpolácia, input handling
- **Discovery** - UDP broadcast pre automatické nájdenie serverov
- **Error handling** - graceful reconnection, error messages

---

## Slide 7: Výsledok
- **Funkčná multiplayer hra** - plne hrateľná
- **Optimalizovaný výkon** - plynulá hra aj s viacerými hráčmi
- **Jednoduché použitie** - intuitívne menu a pripojenie
- **Rozšíriteľné** - ľahko pridať nové funkcie

