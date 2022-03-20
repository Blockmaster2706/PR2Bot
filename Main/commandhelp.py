def command_help(command):
    if   command == "helpslash":
        return "Dieser Befehl. Zeigt Hilfe für den angegebenen Befehl.\nSyntax: /help befehl:(BEFEHL)"
    elif command == "help":
        return "Dieser Befehl. Zeigt Hilfe für den angegebenen Befehl.\nSyntax: help (BEFEHL)"
    elif command == "setlogs":
        return 'Setzt den Channel in dem Befehle gelogt werden. Entfernt den LogChannel falls die Aktion "Entfernen" ist. Channel als ID angeben. Admin only.'
    elif command == "database":
        return "Der Befehl um direkt mit der Datenbank zu interagieren. Nur für den Entwickler."
    elif command == "reminder":
        return "Nutze diesen Befehl um den Bot dich an etwas erinnern zu lassen. Syntax: /reminder erinnerung: (NACHRICHT) stunden: x(optional) minuten: x(optional) sekunden: x(optional)"
    elif command == "commandtoggle":
        return "Schaltet Befehle ein oder aus. Nur für den Entwickler."
    elif command == "pr2":
        return "Nur ein kleiner Test Befehl"
    elif command == "farbrolle":
        return "Gibt dem Nutzer eine Farbrolle oder bearbeitet sie. Die Farbe kann mit oder ohne # genannt werden und ist als Hex Code einzugeben. Der Standard ist Weiß. \nSyntax: $farbrolle (FARBE)"