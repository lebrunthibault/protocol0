interface toBoolean {
    toBool(): boolean
}

type toBooleanClass = new (...args: any[]) => toBoolean

export type { toBooleanClass }
export default toBoolean
