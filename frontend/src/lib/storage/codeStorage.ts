// Remembers the code a student typed for each exercise (key: cpp-platform:code:<exercise id>).
import { read, remove, write } from "./local";

export const loadCode = (exerciseId: string) => read(`code:${exerciseId}`);
export const saveCode = (exerciseId: string, code: string) => write(`code:${exerciseId}`, code);
export const clearCode = (exerciseId: string) => remove(`code:${exerciseId}`);
