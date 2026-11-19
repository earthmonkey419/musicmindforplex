
import {getBackendURL,isTrue,refs} from "$/utils/state"
import {Fragment,memo,useContext,useEffect,useState} from "react"
import {EventLoopContext} from "$/utils/context"
import LucideWifiOff from "lucide-react/dist/esm/icons/wifi-off.mjs"
import {jsx,keyframes} from "@emotion/react"
import env from "$/env.json"








export const DefaultOverlayComponents_04c36749 = /*#__PURE__*/ (() => {
const DefaultOverlayComponents_04c36749 = memo(({}) => {
    const connectErrors = useContext(EventLoopContext)[1];
const toast = refs['__toast'];
const toast_props = ({ ["description"] : ("Check if server is reachable at "+getBackendURL(env.EVENT).href), ["closeButton"] : true, ["duration"] : 120000, ["id"] : "websocket-error" });
const [userDismissed, setUserDismissed] = useState(false);
const [waitedForBackend, setWaitedForBackend] = useState(false);
(useEffect(
() => {
    if (connectErrors.some((error) => error.code === 'hydration_payload_too_large')) {
        toast?.error(((connectErrors.length > 0) ? connectErrors[connectErrors.length - 1].message : ''), {id: "hydration-payload-error", closeButton: true, duration: Infinity});
    } else if ((connectErrors.length >= 2)) {
        if (!userDismissed) {
            toast?.error(("Cannot connect to server: "+((connectErrors.length > 0) ? connectErrors[connectErrors.length - 1].message : '')+"."), {...toast_props, onDismiss: () => setUserDismissed(true)},)
        }
    } else {
        toast?.dismiss("websocket-error");
        setUserDismissed(false);  // after reconnection reset dismissed state
    }
}
, [connectErrors, waitedForBackend]))
    return(
        jsx(Fragment,{},jsx("div",{css:({ ["position"] : "fixed", ["width"] : "100vw", ["height"] : "0" }),title:("Connection Error: "+((connectErrors.length > 0) ? connectErrors[connectErrors.length - 1].message : ''))},jsx(Fragment,{},((connectErrors.length > 0)?(jsx(Fragment,{},jsx(LucideWifiOff,{css:({ ["color"] : "crimson", ["zIndex"] : 9999, ["position"] : "fixed", ["bottom"] : "33px", ["right"] : "33px", ["animation"] : (keyframes({ from: { opacity: 0 }, to: { opacity: 1 } })+" 1s infinite") }),size:32},))):(jsx(Fragment,{},))))),jsx(Fragment,{},))
    )
});
DefaultOverlayComponents_04c36749.displayName = "DefaultOverlayComponents";
return DefaultOverlayComponents_04c36749;
})();
