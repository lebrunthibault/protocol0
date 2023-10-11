function capitalizeFirstLetter(sentence: string) {
  if (sentence.length === 0) {
    return sentence
  }

  return sentence.charAt(0).toUpperCase() + sentence.slice(1)
}

function basename(filename: string): string {
  return filename.split('/').reverse()[0].split("\\").reverse()[0]
}

function notify(message: string) {
  Notification.requestPermission().then(function (result) {
    const notification = new Notification(message)
    setTimeout(() => notification.close(), 2000)
  });
}

export { capitalizeFirstLetter, basename, notify }
