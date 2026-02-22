
init -5 python:
    import time
    import random
    
    class Notification:
        def __init__(self, title, message, icon=None, duration=5.0):
            self.title = title
            self.message = message
            self.icon = icon
            self.duration = duration
            self.start_time = None
            self.visible = True
            self.hide_time = None
            self.id = str(random.randint(100000, 999999))

    class NotificationManager:
        def __init__(self):
            self.queue = []      # Waiting to be shown
            self.active = []     # Currently showing
            self.max_active = 4  # Max notifications on screen
            
        def add(self, message, title="Notification", icon=None, duration=5.0):
            """Add a new notification to the queue."""
            n = Notification(title, message, icon, duration)
            self.queue.append(n)
            self.update()
            
        def update(self):
            """Update active notifications and process queue."""
            current_time = time.time()
            
            # Manage visibility state
            for n in self.active:
                if n.visible and n.start_time and (current_time - n.start_time >= n.duration):
                    n.visible = False
                    n.hide_time = current_time

            # Remove items that have finished animating out (allow 0.6s for 0.5s anim)
            self.active = [n for n in self.active if not (not n.visible and n.hide_time and (current_time - n.hide_time > 0.6))]
            
            # Add from queue if space available (only count visible items towards max)
            visible_count = len([n for n in self.active if n.visible])
            while self.queue and visible_count < self.max_active:
                n = self.queue.pop(0)
                n.start_time = current_time
                n.visible = True
                self.active.append(n)
                visible_count += 1
                
            # Manage screen visibility
            if self.active:
                if not renpy.get_screen("notification_layer"):
                    renpy.show_screen("notification_layer")
            elif not self.queue:
                if renpy.get_screen("notification_layer"):
                    renpy.hide_screen("notification_layer")

    # Initialize global manager
    notification_manager = NotificationManager()

    def add_notification(message, title="Notification", icon=None):
        notification_manager.add(message, title, icon)

transform notification_slide:
    subpixel True
    on show, replace:
        xoffset 400 alpha 0.0
        easein_back 0.5 xoffset 0 alpha 1.0
    on hide:
        easeout_back 0.5 xoffset 400 alpha 0.0

screen notification_layer():
    zorder 500
    style_prefix "notify"
    
    vbox:
        xalign 1.0
        yalign 0.1
        spacing 10
        xoffset -20
        
        for n in reversed(notification_manager.active):
            showif n.visible:
                frame:
                    id n.id
                    at notification_slide
                    
                    padding (15, 10)
                    xsize 350
                    background Frame(Solid("#111a"), 4, 4)
                    
                    hbox:
                        spacing 10
                        if n.icon:
                            add n.icon yalign 0.5 size (40, 40) fit "contain"
                        else:
                            text "ℹ️" size 30 yalign 0.5
                            
                        vbox:
                            text "[n.title]" size 18 bold True color "#ffd700"
                            text "[n.message]" size 16 color "#fff"
    
    timer 0.1 repeat True action Function(notification_manager.update)

# Hook into standard renpy.notify
init 10 python:
    def _notify_hook(message):
        add_notification(message, title="System")
    
    # Overwrite Ren'Py notify to use our system
    renpy.notify = _notify_hook
