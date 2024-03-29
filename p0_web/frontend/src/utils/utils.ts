function capitalizeFirstLetter(sentence: string) {
  if (sentence.length === 0) {
    return sentence
  }

  return sentence.charAt(0).toUpperCase() + sentence.slice(1)
}

function basename(filename: string): string {
  return filename.split('/').reverse()[0].split("\\").reverse()[0]
}

function sceneName(name: string): string {
        const title = name.split("(")[0].trim();
        return title.length > 10 ? title.slice(0, 8) + ".." : title;
}

function notify(message: string, options: NotificationOptions = {}) {
  Notification.requestPermission().then(function () {
    if (options.body) {
      options.requireInteraction = true
    }
    const notification = new Notification(message, options)
    if (!options.body) {
      setTimeout(() => notification.close(), 2000)
    }
  });
}

export { capitalizeFirstLetter, basename, sceneName, notify }
