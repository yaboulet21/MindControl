from pynput.keyboard import Key, Controller

# Créer un contrôleur pour simuler les touches du clavier
keyboard = Controller()

# Simuler la touche multimédia Play/Pause
keyboard.press(Key.media_play_pause)
keyboard.release(Key.media_play_pause)

# Simuler la touche multimédia Next Track
keyboard.press(Key.media_next)
keyboard.release(Key.media_next)

# Simuler la touche multimédia Previous Track
keyboard.press(Key.media_previous)
keyboard.release(Key.media_previous)
