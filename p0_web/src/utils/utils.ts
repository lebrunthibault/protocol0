function capitalizeFirstLetter(sentence: string) {
  if (sentence.length === 0) {
    return sentence
  }

  return sentence.charAt(0).toUpperCase() + sentence.slice(1)
}

function basename(filename: string): string {
  return filename.split('/').reverse()[0].split("\\").reverse()[0]
}

function notify(message: string, options: NotificationOptions = {}) {
  Notification.requestPermission().then(function (result) {
    if (options.body) {
      options.requireInteraction = true
    }
    const notification = new Notification(message, options)
    if (!options.body) {
      setTimeout(() => notification.close(), 2000)
    }
  });
}

export { capitalizeFirstLetter, basename, notify }
