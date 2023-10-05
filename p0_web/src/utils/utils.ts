function capitalizeFirstLetter(sentence: string) {
  if (sentence.length === 0) {
    return sentence
  }

  return sentence.charAt(0).toUpperCase() + sentence.slice(1)
}

function basename(filename: string): string {
  return filename.split('/').reverse()[0].split("\\").reverse()[0]
}

export { capitalizeFirstLetter, basename }
