import { StackHandler } from "@stackframe/stack";
import { stackServerApp } from "../../../stack/server";

export default function Handler(props: any) {
  return <StackHandler app={stackServerApp} {...props} />;
}
