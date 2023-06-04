import ActionInterface from './action_interface'

type ActionClass<A extends ActionInterface> = {new(..._: any): A};

export type { ActionClass }
