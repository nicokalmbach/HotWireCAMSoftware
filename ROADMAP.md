# Roadmap

Die Versionsziele stammen aus der bisherigen Projektplanung. Sie sind geplante
Meilensteine ohne festgelegte Termine. Die Anwendung trägt bereits Version `0.1.0`,
der zugehörige Meilenstein ist aber erst teilweise umgesetzt.

| Zielversion | Schwerpunkt | Stand |
| --- | --- | --- |
| 0.1.0 | Projektstruktur und eine Achse | Grundgerüst vorhanden; Achsensteuerung offen |
| 0.2.0 | Referenzschalter | Geplant |
| 0.3.0 | Referenzfahrt | Geplant |
| 0.4.0 | Mehrere Achsen | Geplant |
| 0.5.0 | Koordinierte Bewegungen | Geplant |
| 0.6.0 | Fehlerbehandlung | Geplant |
| 0.7.0 | Kommunikation | Geplant |
| 0.8.0 | Erweiterte Tests | Geplant |
| 0.9.0 | Beta | Geplant |
| 1.0.0 | Stabile Version | Geplant |

## Nächste Abstimmungen und Schritte

- Mit der Hardwaregruppe Profilformate, Einheiten, Achsen und Maschinenparameter klären.
- Schnittstelle und Zuständigkeiten für die Maschinenkommunikation abstimmen.
  Kommunikation steht bisher bei `0.7.0`; die für frühere Achsenfunktionen nötige
  Schnittstelle muss vorher geklärt werden.
- Anforderungen und Prüfkriterien für den ersten Achsen-Meilenstein festhalten.
- Einen unabhängig von der Maschinensteuerung prüfbaren Profilimport vorbereiten.
  Dessen Zuordnung zu einer Zielversion ist noch offen.

## Begleitende Dokumentation

Bei jedem umgesetzten Schritt den tatsächlichen Stand hier und die Änderungen im
[Changelog](CHANGELOG.md) aktualisieren. Technische Entscheidungen gehören in
[ARCHITECTURE.md](ARCHITECTURE.md); neue Einrichtungs- oder Betriebsanforderungen
in die Installationsanleitung und Fehlerbehebung.
