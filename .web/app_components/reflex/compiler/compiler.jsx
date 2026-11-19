
import {isTrue,refs} from "$/utils/state"
import {Toaster,toast} from "sonner"
import {ColorModeContext} from "$/utils/context"
import {Fragment,memo,useContext,useEffect} from "react"
import {jsx} from "@emotion/react"








export const MemoizedToastProvider_18b15038 = /*#__PURE__*/ (() => {
const MemoizedToastProvider_18b15038 = memo(({}) => {
    const { resolvedColorMode } = useContext(ColorModeContext)
refs['__toast'] = toast
    return(
        jsx(Toaster,{closeButton:false,expand:true,position:"bottom-right",richColors:true,theme:resolvedColorMode},)
    )
});
MemoizedToastProvider_18b15038.displayName = "MemoizedToastProvider";
return MemoizedToastProvider_18b15038;
})();
