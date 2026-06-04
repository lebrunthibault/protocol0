# MIDI mapping mode — knobs configurables, dans l'optique du keymapper

**Statut : backlog / vision.** Pas prioritaire. C'est l'extension MIDI du
gestionnaire de raccourcis : un deuxième « mode de mapping » à côté du keymapper,
qui suit la **même optique** (indépendant du set, déclenche des smart actions,
configurable via l'UI web de l'agent). À reprendre quand le keymapper clavier
(Jalon 2) sera stabilisé.

## Le sujet

Aujourd'hui le mapping des encoders MIDI est **codé en dur** dans des sous-classes
d'`ActionGroupInterface` (cf. `ActionGroupLaunchKeyMini.py` : les 8 encoders CC
21–28 ch.1 → les 8 macros du rack d'instrument de la track sélectionnée). Pour
changer un mapping, il faut éditer le code.

On veut le rendre **configurable**, comme le clavier. Le cas d'usage déclencheur :
permettre à des knobs MIDI de piloter les **N premiers paramètres du device
sélectionné** (jusqu'à 16, pour matcher le nombre de macros d'un Rack Ableton).
C'est exactement le pattern « map encoders to the selected device » de Structure
Void :
<https://midiremotescripts.structure-void.com/guides/cookbook/#map-encoders-to-the-selected-device>.

Le script fait déjà cela à sa manière (LaunchKey Mini → macros), mais figé. L'idée
est de généraliser : un **mode mapping MIDI** où l'on mappe, encoder par encoder,
le **paramètre numéro n** du device Live courant — et plus largement n'importe
quelle smart action — depuis l'UI web.

## Vision (rappel, alignée constitution)

Même mental model que le keymapper, mais l'entrée est un **contrôle MIDI** (CC /
note) au lieu d'une combinaison clavier :

```
  [ contrôle MIDI reçu ]
        │
        ▼
  detection MIDI  ──►  binding resolution  ──►  action  ──►  Live API (LOM)
   (Framework Live)    (config globale)        (paramétrée)
```

Deux propriétés héritées du keymapper, non négociables :

1. **Indépendant du set** — les mappings vivent dans un JSON
   `%APPDATA%\Protocol0\` (machine/user), pas dans le `.als`. Les mêmes knobs
   font la même chose dans tous les sets.
2. **Smart actions discoverable** — un mapping pointe vers une action nommée et
   paramétrée du même catalogue que le clavier. Mapper le « param n du device
   sélectionné » est *une* action parmi d'autres, pas un cas spécial gravé.

## Décision d'archi : la détection MIDI reste **dans le script**

Contrairement au clavier (où la détection est **hors-process** dans l'agent, faute
de pouvoir hooker le clavier global depuis le Python d'Ableton — cf. spike NO-GO
du keymapper), le MIDI **arrive déjà dans Live** via le MIDI Remote Script
framework (`ButtonElement`, `MultiEncoder`, `subject_slot`). Il n'y a aucune raison
de le re-capter hors de Live :

- Le routage « device sélectionné → param n » a besoin du LOM en direct (Song.view,
  track/device sélectionnés). C'est intrinsèquement in-script.
- Le framework gère déjà l'abonnement MIDI (channel/CC/note), le mapping absolu
  0–127 → range de param (cf. `ActionGroupLaunchKeyMini._on_cc`), le
  `component_guard`, l'undo.

→ **L'agent ne fait que la config** : il sert l'UI « MIDI mapping » et écrit le
JSON ; le script lit ce JSON, construit les actions dynamiquement et les attache
aux encoders. C'est la même **couture capture/exécution** que le clavier, juste
avec la capture déjà du bon côté. La frontière HTTP (catalogue d'actions,
discoverable) reste identique.

Conséquence : le keymapper a sa détection dans l'agent, le MIDI mapping a la sienne
dans le script. Les deux **partagent** l'UI de config (agent), le catalogue
d'actions (script) et le principe « config globale hors du set ». C'est cohérent
avec « Decoupled capture / execution » : peu importe *où* on capte, l'action et sa
config sont les mêmes.

## État actuel (code à respecter / réutiliser)

- `application/control_surface/MultiEncoder.py` — encoder : press / long-press /
  scroll, actions = `List[EncoderAction]`, exécutées via `_find_and_execute_action`.
- `application/control_surface/EncoderAction.py` — wrapper callable + `EncoderMoveEnum`
  + undo + Sequence.
- `application/control_surface/ActionGroupInterface.py` — base des groupes ;
  `add_encoder()` ; `configure()` (abstrait, hard-codé par sous-classe aujourd'hui).
- `application/control_surface/group/ActionGroupLaunchKeyMini.py` — **la référence** :
  CC absolu 0–127 → `param.value = param.min + (value/127) * (param.max - param.min)`,
  en écoutant des `ButtonElement` directement (bypass MultiEncoder pour le CC absolu).
- `application/control_surface/ActionGroupFactory.py` — découvre les `ActionGroupInterface`
  par réflexion, instancie si `CHANNEL` défini, appelle `configure()`.
- `shared/Song.py` — `selected_device()`, `selected_track()`, `selected_parameter()`
  (façade stateless, lit Live en direct).
- `domain/lom/device/Device.py` — `parameters: List[DeviceParameter]`,
  `get_parameter_by_name()`.
- `domain/lom/device_parameter/DeviceParameter.py` — `value`/`min`/`max`,
  `scroll(go_next)`, `toggle()`, `reset()`.
- Côté config/catalogue (à calquer) : `domain/shortcut/ShortcutConfigService.py`
  (load/save/upsert atomique sur `shortcuts.json`), `application/http/ActionCatalog.py`
  (catalogue dérivé des `@route`), agent `src/agent/agent/` (UI keymapper + `/api`
  sur `:9010`).

## Architecture cible

```
[knob MIDI]                         ┌──────────── Ableton (remote script) ──────────┐
   │ CC/note                        │  MidiMappingService :                          │
   ▼                                │   - lit %APPDATA%\Protocol0\midi_mappings.json │
ButtonElement / MultiEncoder  ──────►   - construit une action par mapping          │
   │ (framework, abonnement MIDI)   │   - l'attache à l'encoder (configure dynamique)│
   ▼                                │   - résout device/param au moment du move      │
action paramétrée  ─────────────────►  Live API (LOM) : param.value / scroll / smart│
                                    └────────────────────────────────────────────────┘
   UI « MIDI mapping » (agent :9010) ─────►  écrit midi_mappings.json (atomique)
        navigateur, hors Live                 (script relit sur changement de mtime)
```

## Schéma de mapping (esquisse, à figer en todo)

```json
{
  "version": 1,
  "mappings": [
    {
      "channel": 1,
      "control": { "type": "cc", "number": 21 },
      "move": "absolute",
      "action": "device_param",
      "params": { "target": "selected", "param_index": 0 }
    }
  ]
}
```

- `control` : `cc` | `note`, + `number`. `move` : `absolute` (0–127 → range) ou
  `relative`/`scroll` (incrément, comme MultiEncoder).
- `action` : nom du catalogue. Le cas « N premiers params » = action
  `device_param` avec `target` (`selected` au début) + `param_index` (0..15).
  Banque/offset = phase ultérieure.

## Jalons (esquisse)

- **M1 — mapping statique « selected device », piloté par config.** Une action
  `device_param(target="selected", param_index=n)` qui résout
  `Song.selected_device()` → `device.parameters[n]` et applique la valeur (réutilise
  le mapping 0–127 → range de `ActionGroupLaunchKeyMini`). Un `MidiMappingService`
  in-script lit `midi_mappings.json` et attache N encoders (jusqu'à 16). Config
  éditée à la main d'abord — valider end-to-end dans Live avant l'UI.
- **M2 — config via l'UI de l'agent.** Page « MIDI mapping » dans l'agent (à côté
  du keymapper) : liste les contrôles, capture le CC/note entrant, choisit l'action
  + params depuis le catalogue, écrit `midi_mappings.json`. Le script relit sur
  changement de mtime (même mécanique que `shortcuts.json`). Capturer le MIDI
  entrant pour l'UI : soit l'agent ouvre un port MIDI en lecture le temps du
  « learn », soit le script expose le dernier CC reçu via une route — **à trancher
  en todo** (impacte si l'agent touche au MIDI ou non ; garder l'agent MIDI-free si
  possible, via une route `/midi/last` côté script).
- **M3 — smart actions + banks.** Élargir au-delà de `device_param` : n'importe
  quelle action du catalogue mappable sur un knob/bouton. Banques de paramètres
  (offset × 8/16, route `/bank/select`, feedback MIDI out pour afficher la banque).
  Sélecteurs de device au-delà de `selected` (`by_name`, `by_index`, chaîne de rack).

## Points à trancher (en todo)

1. **Capture MIDI pour le « learn » de l'UI** : agent ouvre un port MIDI vs route
   `/midi/last` côté script. Préférence : garder l'agent MIDI-free (cohérent avec
   « l'agent ne fait que la config »).
2. **Absolu vs relatif** par contrôle (knobs endless vs potards) — encodé dans
   `move`. Le LaunchKey envoie de l'absolu ; d'autres surfaces du relatif.
3. **Cohabitation avec les `ActionGroup` hard-codés existants** : migration
   progressive (laisser le LaunchKey hard-codé tant que M1 ne couvre pas tout) vs
   bascule. Ne pas casser l'existant.
4. **Un seul JSON ou deux** : `midi_mappings.json` séparé de `shortcuts.json`
   (probable, schémas différents) mais même dossier `%APPDATA%\Protocol0\`.

## Hors scope (vision)

Feedback MIDI bidirectionnel riche (LED/anneaux), prise en charge fine de chaque
surface du marché, mapping de courbes non linéaires. On vise d'abord le cas
« N premiers params du device sélectionné, configurable », fidèle au cookbook
Structure Void.

## Références

- Structure Void — *Map encoders to the selected device* :
  <https://midiremotescripts.structure-void.com/guides/cookbook/#map-encoders-to-the-selected-device>
- Spec keymapper (la trame à calquer) :
  `docs/specs/done/2026-05-27-keyboard-shortcut-manager-prototype.md`
- `CONSTITUTION.md` §1 « Future direction » (cette vision y est résumée).
