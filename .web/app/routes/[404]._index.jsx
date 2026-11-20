import {Fragment,useEffect} from "react"
import {jsx} from "@emotion/react"





function Component() {


  return (
    jsx(Fragment,{},jsx("span",{},"404: Page not found"),jsx("title",{},"404 - Not Found"),jsx("meta",{content:"The page was not found",name:"description"},),jsx("meta",{content:"favicon.ico",property:"og:image"},))
  )
}
Component.displayName = "Component(404)";

export default Component;
