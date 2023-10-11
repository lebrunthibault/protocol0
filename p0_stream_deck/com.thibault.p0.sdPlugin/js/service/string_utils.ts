const snakeCaseToSpaceCase = (str: string) => str.replace(/_/g, ' ')

function toTitleCase (str: string) {
    return str.replace(
        /\w\S*/g,
        (txt: string) => txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase()
    )
}

const titleMapping: { [key: string]: string; } = {
    AUTO_FILTER_HIGH_PASS: 'HPF',
    AUTO_FILTER_LOW_PASS: 'LPF',
    COMPRESSOR: 'Comp',
    EQ: 'EQ',
    FREE_CLIP: 'Clipper',
    INSERT_DELAY: 'Insert',
    INSERT_REVERB: 'Insert',
    INSERT_DRY_WET: 'Dry / Wet',
    PRO_Q_3: 'Pro-Q 3',
    SERUM_RACK: 'Serum',
    SERUM_BASS: 'Bass',
    SERUM_KEYS: 'Keys',
    SERUM_LEAD: 'Lead',
    SERUM_PLUCK: 'Pluck',
    SYLENTH1_RACK: 'Sylenth1',
    SYLENTH1_BASS: 'Bass',
    SYLENTH1_KEYS: 'Keys',
    SYLENTH1_LEAD: 'Lead',
    SYLENTH1_PLUCK: 'Pluck',
    SUPER_TAP_2: 'ST2',
    SUPER_TAP_6: 'ST6',
    VALHALLA_VINTAGE_VERB: 'Valhalla'
}

const toStreamDeckTitle = (word: string) => {
    if (word in titleMapping) {
        return titleMapping[word]
    }

    let words = word.split(/[\s_-]+/).map(w => w.trim())
    const excludedWords = ['-']
    words = words.filter(w => !excludedWords.includes(w))

    const title = words.join('\n')
    return toTitleCase(snakeCaseToSpaceCase(title))
}

export { toStreamDeckTitle }
