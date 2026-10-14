# Fantasy Kézi v3 – automatikus MKSZ-heti szinkron (kísérleti)

## Feltöltés a GitHubra
A csomag gyökérmappájából töltsd fel a `.github`, `scripts`, `tests`, `FantasyKezi_iPhone_PWA` mappákat **a FantasyKezi repository gyökerébe**, az eredeti alkalmazásmappa fájljait felülírva. Fontos: a `.github` rejtett mappa, Windowsban engedélyezd a rejtett elemek megjelenítését. GitHub webes feltöltésnél a mappastruktúra megőrzése szükséges; ha a böngésző nem kezeli a `.github` mappát, használj GitHub Desktopot vagy VS Code-ot.

## Aktiválás
GitHub → FantasyKezi → Settings → Actions → General → Workflow permissions: Read and write permissions (ha állítható). Ezután Actions → MKSZ heti mérkőzések ellenőrzése → Run workflow. A napi futás 05:20 UTC-kor történik. A sikeres adatgyűjtés részeredménye `FantasyKezi_iPhone_PWA/data/weeks/YYYY-MM-DD.json`, melyet az app frissítéskor letölt. GitHub Pages: main /(root) marad.

## Biztonsági korlát
A szinkron **nem garantált**: az MKSZ JavaScript-oldalának változásai miatt a feldolgozás elakadhat, és a workflow hibával végződhet. Csak olyan egyértelműen felismert mérkőzést ír ki, amelyhez két ismert klub és a konkrét K&H Férfi Liga megnevezés társul. A lista mindig `complete: false` (részleges): ebből nem következtetünk arra, hogy a többi klub biztosan nem játszik. A program a többi klubot ismeretlennek tekinti. A játékospontszámok **nem** frissülnek ettől automatikusan.

## Az app címe
https://antalm15.github.io/FantasyKezi/FantasyKezi_iPhone_PWA/

A korábbi helyi játékos-adatokat nem törli; az új verzióra frissítés után a Safari gyorsítótára miatt szükség lehet az alkalmazás újranyitására.
