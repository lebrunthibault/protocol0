"""Tests de la règle de match Ableton et du parsing de la sortie tasklist."""
from agent import process_check


def test_matches_real_editions():
    assert process_check.matches_ableton("Ableton Live 12 Suite.exe")
    assert process_check.matches_ableton("Ableton Live 11 Standard.exe")
    assert process_check.matches_ableton("Ableton Live 12 Intro.exe")


def test_match_is_case_insensitive():
    assert process_check.matches_ableton("ABLETON LIVE 12 SUITE.EXE")


def test_excludes_ableton_index():
    # L'indexeur de bibliothèque tourne en parallèle du DAW : ne doit PAS matcher.
    assert not process_check.matches_ableton("Ableton Index.exe")


def test_excludes_unrelated_and_bare_name():
    assert not process_check.matches_ableton("chrome.exe")
    assert not process_check.matches_ableton("Ableton Live.exe")  # pas de suffixe d'édition


def test_image_names_parses_csv_column_zero():
    csv_out = (
        '"Ableton Live 12 Suite.exe","1234","Console","1","450,000 K"\n'
        '"Ableton Index.exe","5678","Console","1","12,000 K"\n'
        '"chrome.exe","9012","Console","1","300,000 K"\n'
    )
    names = list(process_check._image_names(csv_out))
    assert names == ["Ableton Live 12 Suite.exe", "Ableton Index.exe", "chrome.exe"]
    # Et la combinaison parse+match ne retient que le DAW :
    assert [n for n in names if process_check.matches_ableton(n)] == [
        "Ableton Live 12 Suite.exe"
    ]
