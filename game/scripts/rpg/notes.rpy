default persistent.unlocked_notes = set()
default note_manager = JournalManager()

init -10 python:
    add_meta_menu_tab("notes", "📘", "Journal", journal_screen,
        selected_tab="notes",
        selected_note=None)

    class Note(object):
        def __init__(self, id, name, content, tags=None):
            self.id = id
            self.name = name
            self.content = content
            self.tags = set(tags or [])

    class NoteManager:
        def __init__(self):
            self.entries = {} # People: name -> description
            self.notes = {} # Notes: id -> Note object
            
        def unlock(self, n, d=None):
            if n not in persistent.met_characters:
                persistent.met_characters.add(n)
                if d: self.register(n, d)
                renpy.notify(f"New Person Met: {n}")
                event_manager.dispatch("CHAR_MET", char=n)
        
        @property
        def met_list(self): 
            return [(n, self.entries.get(n, "No data.")) for n in sorted(persistent.met_characters)]

        def register_note(self, note):
            self.notes[note.id] = note
            
        def unlock_note(self, note_id):
            if note_id in self.notes:
                if persistent.unlocked_notes is None:
                    persistent.unlocked_notes = set()
                
                if note_id not in persistent.unlocked_notes:
                    persistent.unlocked_notes.add(note_id)
                    renpy.notify(f"Note Found: {self.notes[note_id].name}")
                    event_manager.dispatch("NOTE_UNLOCKED", note=note_id)
        
        def get_unlocked_notes(self):
            if persistent.unlocked_notes is None:
                return []
            return [self.notes[nid] for nid in persistent.unlocked_notes if nid in self.notes]

    def reload_note_manager(data):
        note_manager.entries = {}
        note_manager.notes = {}
        for note_id, ndata in data.get("notes", {}).items():
            try:
                note_manager.notes[note_id] = from_dict(Note, ndata, id=note_id)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Note Load Error ({}): {}\n".format(note_id, str(e)))

screen journal_screen():
    vbox:
        spacing 10
        xfill True
        yfill True
        # Sub-tabs
        hbox:
            spacing 10
            xalign 0.5
            textbutton "Notes":
                action SetVariable("selected_journal_tab", "notes")
                style "tab_button"
                text_style "tab_button_text"
                selected (selected_journal_tab == "notes")
            textbutton "People":
                action SetVariable("selected_journal_tab", "people")
                style "tab_button"
                text_style "tab_button_text"
                selected (selected_journal_tab == "people")
        
        null height 10

        if selected_journal_tab == "notes":
            use notes_sub_content
        elif journal_tab == "people":
            use people_sub_content

screen notes_sub_content():
    hbox:
        spacing 20
        xfill True
        yfill True
        # Note List
        frame:
            background "#222"
            xsize 520
            yfill True
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for note in journal_manager.get_unlocked_notes():
                        textbutton "[note.name]":
                            action SetVariable("selected_note", note)
                            xfill True
                            background ("#333" if globals().get("selected_note") == note else "#111")
                            text_style "inventory_item_text"

        # Note Details
        frame:
            background "#222"
            xfill True
            yfill True
            padding (20, 20)
            
            if globals().get("selected_note"):
                $ n = selected_note
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 10
                        text "[n.name]" size 30 color "#ffd700"
                        text "[n.content]" size 22 color "#fff"
            else:
                text "Select a note to read." align (0.5, 0.5) color "#666666"