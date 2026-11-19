
import {ReflexEvent,applyEventActions,isNotNullOrUndefined,isTrue,mergeSlotProps,pyOr,useRegisteredRef} from "$/utils/state"
import {Badge as RadixThemesBadge,Box as RadixThemesBox,Button as RadixThemesButton,Checkbox as RadixThemesCheckbox,Code as RadixThemesCode,Dialog as RadixThemesDialog,DropdownMenu as RadixThemesDropdownMenu,Flex as RadixThemesFlex,Heading as RadixThemesHeading,Link as RadixThemesLink,Progress as RadixThemesProgress,Select as RadixThemesSelect,Table as RadixThemesTable,Text as RadixThemesText,TextArea as RadixThemesTextArea,TextField as RadixThemesTextField} from "@radix-ui/themes"
import {ClientSide,ColorModeContext,addEvents} from "$/utils/context"
import {Fragment,memo,useCallback,useContext,useEffect} from "react"
import {jsx} from "@emotion/react"
import {useStateContext} from "$/utils/context-registry"
import DebounceInput from "react-debounce-input"
import {Link as ReactRouterLink} from "react-router"
import {Bar as RechartsBar,CartesianGrid as RechartsCartesianGrid,Cell as RechartsCell,Legend as RechartsLegend,Line as RechartsLine,Pie as RechartsPie,ResponsiveContainer as RechartsResponsiveContainer,Tooltip as RechartsTooltip,XAxis as RechartsXAxis,YAxis as RechartsYAxis} from "recharts"
import LucideChevronDown from "lucide-react/dist/esm/icons/chevron-down.mjs"
import {PrismAsyncLight as SyntaxHighlighter} from "react-syntax-highlighter"
import oneLight from "react-syntax-highlighter/dist/esm/styles/prism/one-light"
import oneDark from "react-syntax-highlighter/dist/esm/styles/prism/one-dark"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import remarkGfm from "remark-gfm"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"
import rehypeRaw from "rehype-raw"
import rehypeUnwrapImages from "rehype-unwrap-images"

const RechartsBarChart = ClientSide(() => import('recharts').then((mod) => mod.BarChart), "RechartsBarChart")
const RechartsLineChart = ClientSide(() => import('recharts').then((mod) => mod.LineChart), "RechartsLineChart")
const RechartsPieChart = ClientSide(() => import('recharts').then((mod) => mod.PieChart), "RechartsPieChart")


        function ComponentMap_d8b2dcef1196f2645c614da09ad39de0 () {
            const { resolvedColorMode } = useContext(ColorModeContext)
            return (
                ({ ["h1"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h1",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"6",...props},children))), ["h2"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h2",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"5",...props},children))), ["h3"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h3",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"4",...props},children))), ["h4"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h4",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"3",...props},children))), ["h5"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h5",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"2",...props},children))), ["h6"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h6",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"1",...props},children))), ["p"] : (({node, children, ...props}) => (jsx(RadixThemesText,{as:"p",css:({ ["marginTop"] : "1em", ["marginBottom"] : "1em" }),...props},children))), ["ul"] : (({node, children, ...props}) => (jsx("ul",{css:({ ["listStyleType"] : "disc", ["marginTop"] : "1em", ["marginBottom"] : "1em", ["marginLeft"] : "1.5rem", ["direction"] : "column" }),...props},children))), ["ol"] : (({node, children, ...props}) => (jsx("ol",{css:({ ["listStyleType"] : "decimal", ["marginTop"] : "1em", ["marginBottom"] : "1em", ["marginLeft"] : "1.5rem", ["direction"] : "column" }),...props},children))), ["li"] : (({node, children, ...props}) => (jsx("li",{css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),...props},children))), ["a"] : (({node, children, ...props}) => (jsx(RadixThemesLink,{css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),href:"#",...props},children))), ["code"] : (({node, children, ...props}) => (jsx(RadixThemesCode,{...props},children))), ["pre"] : (({node, ...rest}) => { const {node: childNode, className, children: components, ...props} = rest.children.props; const children = String(Array.isArray(components) ? components.join('\n') : components).replace(/\n$/, ''); const match = (className || '').match(/language-(?<lang>.*)/); let _language = match ? match[1] : ''; ;             return jsx(SyntaxHighlighter,{children:children,codeTagProps:({ ["style"] : ({ ["whiteSpace"] : "pre-wrap" }) }),css:({ ["marginTop"] : "1em", ["marginBottom"] : "1em" }),customStyle:({ ["marginTop"] : "1em", ["marginBottom"] : "1em" }),language:_language,style:((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.()) ? oneLight : oneDark),wrapLongLines:true,...props},);         }) })
            )
        }
        




export const Dropdownmenuitem_dropdownmenu__item_4e9c9676ab79b78a919cf172b9a1b2b1_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_4e9c9676ab79b78a919cf172b9a1b2b1_79b11725 = memo(({children, ...rest}) => {
    const on_select_a8086f0e0c5eefd44e24111e0cb81f52 = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/admin", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_a8086f0e0c5eefd44e24111e0cb81f52 }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_4e9c9676ab79b78a919cf172b9a1b2b1_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_4e9c9676ab79b78a919cf172b9a1b2b1_79b11725;
})();

export const Dropdownmenuitem_dropdownmenu__item_761ede4d8667f772cf7a156229505836_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_761ede4d8667f772cf7a156229505836_79b11725 = memo(({children, ...rest}) => {
    const on_select_e0b5bee67f7b919f6682a05fbaa9bc6f = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/db", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_e0b5bee67f7b919f6682a05fbaa9bc6f }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_761ede4d8667f772cf7a156229505836_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_761ede4d8667f772cf7a156229505836_79b11725;
})();

export const Dropdownmenuitem_dropdownmenu__item_9454d499f66c8518d189f5656ca41cd5_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_9454d499f66c8518d189f5656ca41cd5_79b11725 = memo(({children, ...rest}) => {
    const on_select_dcddec7d3d598a63beba8169905259b0 = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/playlist-audit", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_dcddec7d3d598a63beba8169905259b0 }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_9454d499f66c8518d189f5656ca41cd5_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_9454d499f66c8518d189f5656ca41cd5_79b11725;
})();

export const Dropdownmenuitem_dropdownmenu__item_ec8da3997d47f992451b0452eac5ca58_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_ec8da3997d47f992451b0452eac5ca58_79b11725 = memo(({children, ...rest}) => {
    const on_select_3e0a352770194139c24ce23589585312 = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/tests", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_3e0a352770194139c24ce23589585312 }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_ec8da3997d47f992451b0452eac5ca58_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_ec8da3997d47f992451b0452eac5ca58_79b11725;
})();

export const Dropdownmenuitem_dropdownmenu__item_2e11b70bcdd69b041ef274223ff6818a_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_2e11b70bcdd69b041ef274223ff6818a_79b11725 = memo(({children, ...rest}) => {
    const on_select_f828123f0b2b64c30e2d3292ba02fd6f = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/admin#synapse", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_f828123f0b2b64c30e2d3292ba02fd6f }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_2e11b70bcdd69b041ef274223ff6818a_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_2e11b70bcdd69b041ef274223ff6818a_79b11725;
})();

export const Dropdownmenuitem_dropdownmenu__item_28b95f8608ee19f3586e8d7d8f41f4bf_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_28b95f8608ee19f3586e8d7d8f41f4bf_79b11725 = memo(({children, ...rest}) => {
    const on_select_33f3a0c61b6b832ea0f31d5ae52b8de6 = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/logs", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_33f3a0c61b6b832ea0f31d5ae52b8de6 }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_28b95f8608ee19f3586e8d7d8f41f4bf_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_28b95f8608ee19f3586e8d7d8f41f4bf_79b11725;
})();

export const Dropdownmenuitem_dropdownmenu__item_6031994ccb1e0ff89d90f636d3e7779e_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_6031994ccb1e0ff89d90f636d3e7779e_79b11725 = memo(({children, ...rest}) => {
    const on_select_fbba0380b27a0ff9a2b0b8056d2bdd01 = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/guide", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_fbba0380b27a0ff9a2b0b8056d2bdd01 }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_6031994ccb1e0ff89d90f636d3e7779e_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_6031994ccb1e0ff89d90f636d3e7779e_79b11725;
})();

export const Dropdownmenuitem_dropdownmenu__item_4773552c777e96eeffa74c90b749b63b_79b11725 = /*#__PURE__*/ (() => {
const Dropdownmenuitem_dropdownmenu__item_4773552c777e96eeffa74c90b749b63b_79b11725 = memo(({children, ...rest}) => {
    const on_select_f804399826ea8e3bfb0da7ddf237863f = useCallback(((...args) => (addEvents([(ReflexEvent("_redirect", ({ ["path"] : "/update", ["external"] : false, ["popup"] : false, ["replace"] : false }), ({  })))], args, ({  })))), [])
    return(
        jsx(RadixThemesDropdownMenu.Item,{...mergeSlotProps(rest, ({ onSelect:on_select_f804399826ea8e3bfb0da7ddf237863f }))},children)
    )
});
Dropdownmenuitem_dropdownmenu__item_4773552c777e96eeffa74c90b749b63b_79b11725.displayName = "DropdownMenuItem";
return Dropdownmenuitem_dropdownmenu__item_4773552c777e96eeffa74c90b749b63b_79b11725;
})();

export const Cond_comp_5fd47f2b39bc5da842756d022c27ce1e_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_5fd47f2b39bc5da842756d022c27ce1e_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "light"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_5fd47f2b39bc5da842756d022c27ce1e_79b11725.displayName = "Cond";
return Cond_comp_5fd47f2b39bc5da842756d022c27ce1e_79b11725;
})();

export const Button_button_54d3ffcbdf096982557499a471966035_79b11725 = /*#__PURE__*/ (() => {
const Button_button_54d3ffcbdf096982557499a471966035_79b11725 = memo(({children, ...rest}) => {
    const on_click_0fd0436b1ff335e4a5f0f8142b915ae4 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_theme", ({ ["value"] : "light" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ "aria-label":"Light theme", "aria-pressed":(reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "light"?.valueOf?.()), className:((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "light"?.valueOf?.()) ? "palette-option is-selected" : "palette-option"), onClick:on_click_0fd0436b1ff335e4a5f0f8142b915ae4 }))},children)
    )
});
Button_button_54d3ffcbdf096982557499a471966035_79b11725.displayName = "Button";
return Button_button_54d3ffcbdf096982557499a471966035_79b11725;
})();

export const Cond_comp_92b2924f08e508bc1c920da8cf28b44b_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_92b2924f08e508bc1c920da8cf28b44b_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "parchment"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_92b2924f08e508bc1c920da8cf28b44b_79b11725.displayName = "Cond";
return Cond_comp_92b2924f08e508bc1c920da8cf28b44b_79b11725;
})();

export const Button_button_714e9afaf295f9667af1957fb34b4715_79b11725 = /*#__PURE__*/ (() => {
const Button_button_714e9afaf295f9667af1957fb34b4715_79b11725 = memo(({children, ...rest}) => {
    const on_click_97e1fa9c507a6db4ea61467fb253e95e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_theme", ({ ["value"] : "parchment" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ "aria-label":"Parchment theme", "aria-pressed":(reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "parchment"?.valueOf?.()), className:((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "parchment"?.valueOf?.()) ? "palette-option is-selected" : "palette-option"), onClick:on_click_97e1fa9c507a6db4ea61467fb253e95e }))},children)
    )
});
Button_button_714e9afaf295f9667af1957fb34b4715_79b11725.displayName = "Button";
return Button_button_714e9afaf295f9667af1957fb34b4715_79b11725;
})();

export const Cond_comp_1d80e089ee39b135d66a0810ddd4e3c3_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_1d80e089ee39b135d66a0810ddd4e3c3_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "midnight"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_1d80e089ee39b135d66a0810ddd4e3c3_79b11725.displayName = "Cond";
return Cond_comp_1d80e089ee39b135d66a0810ddd4e3c3_79b11725;
})();

export const Button_button_0f1b01ec66e0962474ab50ab744e10da_79b11725 = /*#__PURE__*/ (() => {
const Button_button_0f1b01ec66e0962474ab50ab744e10da_79b11725 = memo(({children, ...rest}) => {
    const on_click_f1978fff4ce2ff15bc3b6d3c17559372 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_theme", ({ ["value"] : "midnight" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ "aria-label":"Midnight theme", "aria-pressed":(reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "midnight"?.valueOf?.()), className:((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "midnight"?.valueOf?.()) ? "palette-option is-selected" : "palette-option"), onClick:on_click_f1978fff4ce2ff15bc3b6d3c17559372 }))},children)
    )
});
Button_button_0f1b01ec66e0962474ab50ab744e10da_79b11725.displayName = "Button";
return Button_button_0f1b01ec66e0962474ab50ab744e10da_79b11725;
})();

export const Cond_comp_37e5da3df2a1c613aa066df061f5a529_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_37e5da3df2a1c613aa066df061f5a529_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "ocean"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_37e5da3df2a1c613aa066df061f5a529_79b11725.displayName = "Cond";
return Cond_comp_37e5da3df2a1c613aa066df061f5a529_79b11725;
})();

export const Button_button_a2975572f7600968b4f62e0732f907a3_79b11725 = /*#__PURE__*/ (() => {
const Button_button_a2975572f7600968b4f62e0732f907a3_79b11725 = memo(({children, ...rest}) => {
    const on_click_a39d0acd76b9db48a8cf7384ebeb99e7 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_theme", ({ ["value"] : "ocean" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ "aria-label":"Ocean theme", "aria-pressed":(reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "ocean"?.valueOf?.()), className:((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "ocean"?.valueOf?.()) ? "palette-option is-selected" : "palette-option"), onClick:on_click_a39d0acd76b9db48a8cf7384ebeb99e7 }))},children)
    )
});
Button_button_a2975572f7600968b4f62e0732f907a3_79b11725.displayName = "Button";
return Button_button_a2975572f7600968b4f62e0732f907a3_79b11725;
})();

export const Cond_comp_94ad774c9147c95dda6cf46727fb64ba_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_94ad774c9147c95dda6cf46727fb64ba_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "forest"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_94ad774c9147c95dda6cf46727fb64ba_79b11725.displayName = "Cond";
return Cond_comp_94ad774c9147c95dda6cf46727fb64ba_79b11725;
})();

export const Button_button_e623265bead9f17b00590237409905b8_79b11725 = /*#__PURE__*/ (() => {
const Button_button_e623265bead9f17b00590237409905b8_79b11725 = memo(({children, ...rest}) => {
    const on_click_4a5ad8fe5d551c530ea0215370e9ecf1 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_theme", ({ ["value"] : "forest" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ "aria-label":"Forest theme", "aria-pressed":(reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "forest"?.valueOf?.()), className:((reflex___state____state__musicmind_ui___state___ui.theme_rx_state_?.valueOf?.() === "forest"?.valueOf?.()) ? "palette-option is-selected" : "palette-option"), onClick:on_click_4a5ad8fe5d551c530ea0215370e9ecf1 }))},children)
    )
});
Button_button_e623265bead9f17b00590237409905b8_79b11725.displayName = "Button";
return Button_button_e623265bead9f17b00590237409905b8_79b11725;
})();

export const Bare_comp_41a319f21e869bbcf2c7124dd4f09049_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_41a319f21e869bbcf2c7124dd4f09049_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.message_rx_state_
    )
});
Bare_comp_41a319f21e869bbcf2c7124dd4f09049_79b11725.displayName = "Bare";
return Bare_comp_41a319f21e869bbcf2c7124dd4f09049_79b11725;
})();

export const Cond_comp_430e7b8d2faa2a14df0e6a8ed3eed8d9_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_430e7b8d2faa2a14df0e6a8ed3eed8d9_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (!((reflex___state____state__musicmind_ui___state___ui.message_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_430e7b8d2faa2a14df0e6a8ed3eed8d9_79b11725.displayName = "Cond";
return Cond_comp_430e7b8d2faa2a14df0e6a8ed3eed8d9_79b11725;
})();

export const Debounceinput_debounceinput_277781ded44b05268c700e685839203d_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_277781ded44b05268c700e685839203d_79b11725 = memo(({children, ...rest}) => {
    const on_change_783799dbd546e9f7f2276d066de4ddd6 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_prompt", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ css:({ ["width"] : "100%" }), debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_783799dbd546e9f7f2276d066de4ddd6, placeholder:"sunny day driving with the windows down\u2026", size:"3", value:(isNotNullOrUndefined(reflex___state____state__musicmind_ui___state___ui.prompt_rx_state_) ? reflex___state____state__musicmind_ui___state___ui.prompt_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_277781ded44b05268c700e685839203d_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_277781ded44b05268c700e685839203d_79b11725;
})();

export const Button_button_adc19cda049985c2c7809f7c462000e3_79b11725 = /*#__PURE__*/ (() => {
const Button_button_adc19cda049985c2c7809f7c462000e3_79b11725 = memo(({children, ...rest}) => {
    const on_click_2382b99859029af016dfc1e8bfa5dc09 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.preview", ({  }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:reflex___state____state__musicmind_ui___state___ui.busy_rx_state_, onClick:on_click_2382b99859029af016dfc1e8bfa5dc09 }))},children)
    )
});
Button_button_adc19cda049985c2c7809f7c462000e3_79b11725.displayName = "Button";
return Button_button_adc19cda049985c2c7809f7c462000e3_79b11725;
})();

export const Cond_comp_2f6ad1123c08305acd7b8d19d884ad22_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_2f6ad1123c08305acd7b8d19d884ad22_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.filters_open_rx_state_?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_2f6ad1123c08305acd7b8d19d884ad22_79b11725.displayName = "Cond";
return Cond_comp_2f6ad1123c08305acd7b8d19d884ad22_79b11725;
})();

export const Button_button_20a78d44142f4fce4441f91fbdc07b74_79b11725 = /*#__PURE__*/ (() => {
const Button_button_20a78d44142f4fce4441f91fbdc07b74_79b11725 = memo(({children, ...rest}) => {
    const on_click_d97ec0b0597c3075e9f2d5fd556b1ea8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_filters", ({  }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ "aria-expanded":reflex___state____state__musicmind_ui___state___ui.filters_open_rx_state_, className:"tune-search-button", onClick:on_click_d97ec0b0597c3075e9f2d5fd556b1ea8, variant:"outline" }))},children)
    )
});
Button_button_20a78d44142f4fce4441f91fbdc07b74_79b11725.displayName = "Button";
return Button_button_20a78d44142f4fce4441f91fbdc07b74_79b11725;
})();

export const Selectroot_select__root_9109d085f23944311bf2c81e183f8a6c_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_9109d085f23944311bf2c81e183f8a6c_79b11725 = memo(({children, ...rest}) => {
    const on_change_e5ada2cf3d9def372c303e4319a78b81 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "order", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_e5ada2cf3d9def372c303e4319a78b81, value:(isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["order"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["order"] : "BPM flow") }))},children)
    )
});
Selectroot_select__root_9109d085f23944311bf2c81e183f8a6c_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_9109d085f23944311bf2c81e183f8a6c_79b11725;
})();

export const Bare_comp_a9616ca1efd6c3d829a194cf82b7c4bb_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_a9616ca1efd6c3d829a194cf82b7c4bb_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (() => { switch (JSON.stringify((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["order"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["order"] : "BPM flow"))) {case JSON.stringify("BPM ascending"):  return ("Start slow and build steadily.");  break;case JSON.stringify("BPM descending"):  return ("Start fast and ease down.");  break;case JSON.stringify("Best match"):  return ("Keep the search ranking.");  break;default:  return ("Rise to a peak, then wind down. Tracks without BPM go last.");  break;};})()
    )
});
Bare_comp_a9616ca1efd6c3d829a194cf82b7c4bb_79b11725.displayName = "Bare";
return Bare_comp_a9616ca1efd6c3d829a194cf82b7c4bb_79b11725;
})();

export const Button_button_6a245bccb5ebd03e8d52605eff2a6f5e_79b11725 = /*#__PURE__*/ (() => {
const Button_button_6a245bccb5ebd03e8d52605eff2a6f5e_79b11725 = memo(({children, ...rest}) => {
    const on_click_932a6b4d74c5f27b947540f28b6315f2 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter_section", ({ ["value"] : "Sound" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ className:((reflex___state____state__musicmind_ui___state___ui.filter_section_rx_state_?.valueOf?.() === "Sound"?.valueOf?.()) ? "filter-tab is-active" : "filter-tab"), onClick:on_click_932a6b4d74c5f27b947540f28b6315f2, variant:"ghost" }))},children)
    )
});
Button_button_6a245bccb5ebd03e8d52605eff2a6f5e_79b11725.displayName = "Button";
return Button_button_6a245bccb5ebd03e8d52605eff2a6f5e_79b11725;
})();

export const Button_button_3e708c7911f5eae95758b42c2e0134a8_79b11725 = /*#__PURE__*/ (() => {
const Button_button_3e708c7911f5eae95758b42c2e0134a8_79b11725 = memo(({children, ...rest}) => {
    const on_click_628f23f7ba0182979241286541b196db = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter_section", ({ ["value"] : "Context" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ className:((reflex___state____state__musicmind_ui___state___ui.filter_section_rx_state_?.valueOf?.() === "Context"?.valueOf?.()) ? "filter-tab is-active" : "filter-tab"), onClick:on_click_628f23f7ba0182979241286541b196db, variant:"ghost" }))},children)
    )
});
Button_button_3e708c7911f5eae95758b42c2e0134a8_79b11725.displayName = "Button";
return Button_button_3e708c7911f5eae95758b42c2e0134a8_79b11725;
})();

export const Button_button_1aab54306cfe0ea559da1cb32be294b8_79b11725 = /*#__PURE__*/ (() => {
const Button_button_1aab54306cfe0ea559da1cb32be294b8_79b11725 = memo(({children, ...rest}) => {
    const on_click_261a2405919a17f7b193168365b5eb6f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter_section", ({ ["value"] : "Limits" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ className:((reflex___state____state__musicmind_ui___state___ui.filter_section_rx_state_?.valueOf?.() === "Limits"?.valueOf?.()) ? "filter-tab is-active" : "filter-tab"), onClick:on_click_261a2405919a17f7b193168365b5eb6f, variant:"ghost" }))},children)
    )
});
Button_button_1aab54306cfe0ea559da1cb32be294b8_79b11725.displayName = "Button";
return Button_button_1aab54306cfe0ea559da1cb32be294b8_79b11725;
})();

export const Foreach_comp_e49b295d5bb13ec9fbc8bd2bcc854ddb_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_e49b295d5bb13ec9fbc8bd2bcc854ddb_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.genre_names_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_))))
    )
});
Foreach_comp_e49b295d5bb13ec9fbc8bd2bcc854ddb_79b11725.displayName = "Foreach";
return Foreach_comp_e49b295d5bb13ec9fbc8bd2bcc854ddb_79b11725;
})();

export const Selectroot_select__root_bb1ffa452f2075564ceeaa93a7478b2a_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_bb1ffa452f2075564ceeaa93a7478b2a_79b11725 = memo(({children, ...rest}) => {
    const on_change_3d20b215224ea54440fcc615b86e2e2d = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "genre", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_3d20b215224ea54440fcc615b86e2e2d, value:(isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["genre"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["genre"] : "") }))},children)
    )
});
Selectroot_select__root_bb1ffa452f2075564ceeaa93a7478b2a_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_bb1ffa452f2075564ceeaa93a7478b2a_79b11725;
})();

export const Debounceinput_debounceinput_34c11447724c5aa81b7d33a4643ac1ff_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_34c11447724c5aa81b7d33a4643ac1ff_79b11725 = memo(({children, ...rest}) => {
    const on_change_a362b23f61512d3b66c80f5c41d63ea3 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "bpm_min", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_a362b23f61512d3b66c80f5c41d63ea3, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_min"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_min"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_min"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_min"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_34c11447724c5aa81b7d33a4643ac1ff_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_34c11447724c5aa81b7d33a4643ac1ff_79b11725;
})();

export const Debounceinput_debounceinput_2c6d651f8925b67cb3b3c8892391081f_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_2c6d651f8925b67cb3b3c8892391081f_79b11725 = memo(({children, ...rest}) => {
    const on_change_d8d2e57d1a3eaa1b955991cafc78e0ca = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "bpm_max", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_d8d2e57d1a3eaa1b955991cafc78e0ca, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_max"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_max"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_max"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["bpm_max"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_2c6d651f8925b67cb3b3c8892391081f_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_2c6d651f8925b67cb3b3c8892391081f_79b11725;
})();

export const Selectroot_select__root_e66c9c1941d16aaab93c64bfe6ce658b_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_e66c9c1941d16aaab93c64bfe6ce658b_79b11725 = memo(({children, ...rest}) => {
    const on_change_19c10b2aa0dfd12af6e6b66517cf84a6 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "danceability", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_19c10b2aa0dfd12af6e6b66517cf84a6, value:(isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["danceability"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["danceability"] : "") }))},children)
    )
});
Selectroot_select__root_e66c9c1941d16aaab93c64bfe6ce658b_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_e66c9c1941d16aaab93c64bfe6ce658b_79b11725;
})();

export const Debounceinput_debounceinput_6c8f4a201c6dd4493cc6e505c11ff4d0_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_6c8f4a201c6dd4493cc6e505c11ff4d0_79b11725 = memo(({children, ...rest}) => {
    const on_change_c79900ebd2a3531afe5a78aefe1460e3 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "vocal_tolerance", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_c79900ebd2a3531afe5a78aefe1460e3, placeholder:"0.55", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["vocal_tolerance"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["vocal_tolerance"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["vocal_tolerance"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["vocal_tolerance"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_6c8f4a201c6dd4493cc6e505c11ff4d0_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_6c8f4a201c6dd4493cc6e505c11ff4d0_79b11725;
})();

export const Checkbox_checkbox_206a44cae12ed5c9d4bc08ec41f83ec6_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_206a44cae12ed5c9d4bc08ec41f83ec6_79b11725 = memo(({children, ...rest}) => {
    const on_change_0bc12ad1665b27702009064d10ed0d7b = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_instrumental", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ checked:reflex___state____state__musicmind_ui___state___ui.instrumental_rx_state_, onCheckedChange:on_change_0bc12ad1665b27702009064d10ed0d7b, size:"2" }))},)
    )
});
Checkbox_checkbox_206a44cae12ed5c9d4bc08ec41f83ec6_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_206a44cae12ed5c9d4bc08ec41f83ec6_79b11725;
})();

export const Cond_comp_ec6a7ab6804e050c8361804bbedf425f_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_ec6a7ab6804e050c8361804bbedf425f_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.genre_families_open_rx_state_?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_ec6a7ab6804e050c8361804bbedf425f_79b11725.displayName = "Cond";
return Cond_comp_ec6a7ab6804e050c8361804bbedf425f_79b11725;
})();

export const Button_button_b688f98574df5b5ace593c4fcedb42f9_79b11725 = /*#__PURE__*/ (() => {
const Button_button_b688f98574df5b5ace593c4fcedb42f9_79b11725 = memo(({children, ...rest}) => {
    const on_click_de139796b997d7a1f64a31544fe13a8a = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_genre_families", ({  }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ "aria-expanded":reflex___state____state__musicmind_ui___state___ui.genre_families_open_rx_state_, className:"genre-families-toggle", onClick:on_click_de139796b997d7a1f64a31544fe13a8a, variant:"ghost" }))},children)
    )
});
Button_button_b688f98574df5b5ace593c4fcedb42f9_79b11725.displayName = "Button";
return Button_button_b688f98574df5b5ace593c4fcedb42f9_79b11725;
})();

export const Bare_comp_0b0757428c74450ea1043db64b2eae74_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_0b0757428c74450ea1043db64b2eae74_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (JSON.stringify(reflex___state____state__musicmind_ui___state___ui.buckets_rx_state_.length))
    )
});
Bare_comp_0b0757428c74450ea1043db64b2eae74_79b11725.displayName = "Bare";
return Bare_comp_0b0757428c74450ea1043db64b2eae74_79b11725;
})();

export const Cond_comp_89fc4124ad42c6d0a55f283ae4f611a2_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_89fc4124ad42c6d0a55f283ae4f611a2_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.buckets_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_89fc4124ad42c6d0a55f283ae4f611a2_79b11725.displayName = "Cond";
return Cond_comp_89fc4124ad42c6d0a55f283ae4f611a2_79b11725;
})();

export const Checkbox_checkbox_d2a76c0268884b1d08d58796a44befe9_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_d2a76c0268884b1d08d58796a44befe9_79b11725 = memo(({children, ...rest}) => {
    const on_change_c1165e8e9971968ee89c857663acc975 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "New Wave / Post-Punk / Synth", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_c1165e8e9971968ee89c857663acc975, size:"2" }))},)
    )
});
Checkbox_checkbox_d2a76c0268884b1d08d58796a44befe9_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_d2a76c0268884b1d08d58796a44befe9_79b11725;
})();

export const Checkbox_checkbox_aeacc8837435edbb400a4bf1b566fb79_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_aeacc8837435edbb400a4bf1b566fb79_79b11725 = memo(({children, ...rest}) => {
    const on_change_1d3db8b29c8f36df6f82dd7e9f8a552e = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Psych / Art Rock / Experimental", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_1d3db8b29c8f36df6f82dd7e9f8a552e, size:"2" }))},)
    )
});
Checkbox_checkbox_aeacc8837435edbb400a4bf1b566fb79_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_aeacc8837435edbb400a4bf1b566fb79_79b11725;
})();

export const Checkbox_checkbox_9c330fb624b97d08e1a5b0a9571ec0c7_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_9c330fb624b97d08e1a5b0a9571ec0c7_79b11725 = memo(({children, ...rest}) => {
    const on_change_6930eaa0103f2fbe973b0fef320979a1 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Classic / Garage / Alt / Punk Rock", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_6930eaa0103f2fbe973b0fef320979a1, size:"2" }))},)
    )
});
Checkbox_checkbox_9c330fb624b97d08e1a5b0a9571ec0c7_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_9c330fb624b97d08e1a5b0a9571ec0c7_79b11725;
})();

export const Checkbox_checkbox_b385acab19532a8bd3947de78fd4854a_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_b385acab19532a8bd3947de78fd4854a_79b11725 = memo(({children, ...rest}) => {
    const on_change_22f60145a439238ac8f479566b9a8493 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Soul / Funk / R&B", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_22f60145a439238ac8f479566b9a8493, size:"2" }))},)
    )
});
Checkbox_checkbox_b385acab19532a8bd3947de78fd4854a_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_b385acab19532a8bd3947de78fd4854a_79b11725;
})();

export const Checkbox_checkbox_692e347eacc12296e8332e3455326a6e_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_692e347eacc12296e8332e3455326a6e_79b11725 = memo(({children, ...rest}) => {
    const on_change_92228decd8296efc5647925f6d7e0639 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Jazz", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_92228decd8296efc5647925f6d7e0639, size:"2" }))},)
    )
});
Checkbox_checkbox_692e347eacc12296e8332e3455326a6e_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_692e347eacc12296e8332e3455326a6e_79b11725;
})();

export const Checkbox_checkbox_cc949ff8ee6ba19c8ddff6351bbfb015_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_cc949ff8ee6ba19c8ddff6351bbfb015_79b11725 = memo(({children, ...rest}) => {
    const on_change_fa5ec6170f5667049509dc7d34ca624b = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "World / Reggae / Latin / Afro", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_fa5ec6170f5667049509dc7d34ca624b, size:"2" }))},)
    )
});
Checkbox_checkbox_cc949ff8ee6ba19c8ddff6351bbfb015_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_cc949ff8ee6ba19c8ddff6351bbfb015_79b11725;
})();

export const Checkbox_checkbox_48a4f37685bb3539086f2d33d2811db6_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_48a4f37685bb3539086f2d33d2811db6_79b11725 = memo(({children, ...rest}) => {
    const on_change_e5d367a9b4da059a413e151fd1db1832 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Hip-Hop / Rap", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_e5d367a9b4da059a413e151fd1db1832, size:"2" }))},)
    )
});
Checkbox_checkbox_48a4f37685bb3539086f2d33d2811db6_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_48a4f37685bb3539086f2d33d2811db6_79b11725;
})();

export const Checkbox_checkbox_9eb0d4b48ad233ae29c6bc66eafbab4d_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_9eb0d4b48ad233ae29c6bc66eafbab4d_79b11725 = memo(({children, ...rest}) => {
    const on_change_468843a56d7f49bcb4f525a1a38aaf0a = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Pop", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_468843a56d7f49bcb4f525a1a38aaf0a, size:"2" }))},)
    )
});
Checkbox_checkbox_9eb0d4b48ad233ae29c6bc66eafbab4d_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_9eb0d4b48ad233ae29c6bc66eafbab4d_79b11725;
})();

export const Checkbox_checkbox_9232d533d0938e0d91855ec991bdcd7d_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_9232d533d0938e0d91855ec991bdcd7d_79b11725 = memo(({children, ...rest}) => {
    const on_change_e10b1abc51372d589c0ded248a3be984 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Classical / Orchestral / Cinematic", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_e10b1abc51372d589c0ded248a3be984, size:"2" }))},)
    )
});
Checkbox_checkbox_9232d533d0938e0d91855ec991bdcd7d_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_9232d533d0938e0d91855ec991bdcd7d_79b11725;
})();

export const Checkbox_checkbox_0994822df01c09a232f1cb8b4778989f_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_0994822df01c09a232f1cb8b4778989f_79b11725 = memo(({children, ...rest}) => {
    const on_change_3dd353309928e468df23a7f4ca8fd695 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Folk / Singer-Songwriter / Acoustic / Blues", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_3dd353309928e468df23a7f4ca8fd695, size:"2" }))},)
    )
});
Checkbox_checkbox_0994822df01c09a232f1cb8b4778989f_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_0994822df01c09a232f1cb8b4778989f_79b11725;
})();

export const Checkbox_checkbox_6fc9042c5806b0c12b4f29c8b46f346a_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_6fc9042c5806b0c12b4f29c8b46f346a_79b11725 = memo(({children, ...rest}) => {
    const on_change_6253fa4cb1e22c4af8e55e1a01ba6517 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Country / Americana / Bluegrass", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_6253fa4cb1e22c4af8e55e1a01ba6517, size:"2" }))},)
    )
});
Checkbox_checkbox_6fc9042c5806b0c12b4f29c8b46f346a_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_6fc9042c5806b0c12b4f29c8b46f346a_79b11725;
})();

export const Checkbox_checkbox_481b1c31b5b678e1fef444cce8e7185e_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_481b1c31b5b678e1fef444cce8e7185e_79b11725 = memo(({children, ...rest}) => {
    const on_change_27c85b9558251114911d03e84da0564e = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Electronic / House / Techno / Downtempo", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_27c85b9558251114911d03e84da0564e, size:"2" }))},)
    )
});
Checkbox_checkbox_481b1c31b5b678e1fef444cce8e7185e_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_481b1c31b5b678e1fef444cce8e7185e_79b11725;
})();

export const Checkbox_checkbox_d18845a89ab9e1d7c4a9c270ef683a28_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_d18845a89ab9e1d7c4a9c270ef683a28_79b11725 = memo(({children, ...rest}) => {
    const on_change_176a01cfd03e4507cbe87b7a3c79dd26 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Gospel", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_176a01cfd03e4507cbe87b7a3c79dd26, size:"2" }))},)
    )
});
Checkbox_checkbox_d18845a89ab9e1d7c4a9c270ef683a28_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_d18845a89ab9e1d7c4a9c270ef683a28_79b11725;
})();

export const Checkbox_checkbox_c5a04c3a00379a6030194961fac7e604_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_c5a04c3a00379a6030194961fac7e604_79b11725 = memo(({children, ...rest}) => {
    const on_change_22e0a5eca40fb222e8d71a16caf124a6 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_bucket", ({ ["bucket"] : "Chant / Choral / Sacred", ["enabled"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ onCheckedChange:on_change_22e0a5eca40fb222e8d71a16caf124a6, size:"2" }))},)
    )
});
Checkbox_checkbox_c5a04c3a00379a6030194961fac7e604_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_c5a04c3a00379a6030194961fac7e604_79b11725;
})();

export const Cond_comp_be29cecc864b6a78ff6c63e6e146d4d6_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_be29cecc864b6a78ff6c63e6e146d4d6_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.filter_section_rx_state_?.valueOf?.() === "Sound"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_be29cecc864b6a78ff6c63e6e146d4d6_79b11725.displayName = "Cond";
return Cond_comp_be29cecc864b6a78ff6c63e6e146d4d6_79b11725;
})();

export const Debounceinput_debounceinput_03623a87e533ed5341ac9f8708df6c43_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_03623a87e533ed5341ac9f8708df6c43_79b11725 = memo(({children, ...rest}) => {
    const on_change_9c939b10b479e09aeb0835819ec0cc83 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "min_year", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_9c939b10b479e09aeb0835819ec0cc83, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_year"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_year"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_year"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_year"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_03623a87e533ed5341ac9f8708df6c43_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_03623a87e533ed5341ac9f8708df6c43_79b11725;
})();

export const Debounceinput_debounceinput_315cb8dc9984a310cc1ef33b3190f3e3_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_315cb8dc9984a310cc1ef33b3190f3e3_79b11725 = memo(({children, ...rest}) => {
    const on_change_fe09debcc6f39c81b3f181df676a9dd7 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "max_year", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_fe09debcc6f39c81b3f181df676a9dd7, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_year"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_year"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_year"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_year"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_315cb8dc9984a310cc1ef33b3190f3e3_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_315cb8dc9984a310cc1ef33b3190f3e3_79b11725;
})();

export const Foreach_comp_e20322088977ca38fd3ce17ce88e3abf_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_e20322088977ca38fd3ce17ce88e3abf_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.country_names_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_))))
    )
});
Foreach_comp_e20322088977ca38fd3ce17ce88e3abf_79b11725.displayName = "Foreach";
return Foreach_comp_e20322088977ca38fd3ce17ce88e3abf_79b11725;
})();

export const Selectroot_select__root_51c0b972c8f9e1ab3e53c7f780fa7f2e_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_51c0b972c8f9e1ab3e53c7f780fa7f2e_79b11725 = memo(({children, ...rest}) => {
    const on_change_5ecad510726af51f0f557807972b8a75 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "country", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_5ecad510726af51f0f557807972b8a75, value:(isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["country"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["country"] : "") }))},children)
    )
});
Selectroot_select__root_51c0b972c8f9e1ab3e53c7f780fa7f2e_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_51c0b972c8f9e1ab3e53c7f780fa7f2e_79b11725;
})();

export const Selectroot_select__root_1b19610be22511a45bd1f2772863ad01_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_1b19610be22511a45bd1f2772863ad01_79b11725 = memo(({children, ...rest}) => {
    const on_change_78833aa2bf574f86e9c8bdef4d318668 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "gender", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_78833aa2bf574f86e9c8bdef4d318668, value:(isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["gender"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["gender"] : "") }))},children)
    )
});
Selectroot_select__root_1b19610be22511a45bd1f2772863ad01_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_1b19610be22511a45bd1f2772863ad01_79b11725;
})();

export const Selectroot_select__root_343563ac880836125b6a5c8d8f491cbd_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_343563ac880836125b6a5c8d8f491cbd_79b11725 = memo(({children, ...rest}) => {
    const on_change_62820e0a6fe95b7b9c9014064a0ed1af = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "era", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_62820e0a6fe95b7b9c9014064a0ed1af, value:(isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["era"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["era"] : "") }))},children)
    )
});
Selectroot_select__root_343563ac880836125b6a5c8d8f491cbd_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_343563ac880836125b6a5c8d8f491cbd_79b11725;
})();

export const Cond_comp_d9c3d5cbb5d666f18dba713af1f9efe5_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_d9c3d5cbb5d666f18dba713af1f9efe5_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.filter_section_rx_state_?.valueOf?.() === "Context"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_d9c3d5cbb5d666f18dba713af1f9efe5_79b11725.displayName = "Cond";
return Cond_comp_d9c3d5cbb5d666f18dba713af1f9efe5_79b11725;
})();

export const Debounceinput_debounceinput_a592af01d1baaf91e422593362f99f92_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_a592af01d1baaf91e422593362f99f92_79b11725 = memo(({children, ...rest}) => {
    const on_change_fdb86babc7d17bcb09e1e5bcb8857f2c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "limit", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_fdb86babc7d17bcb09e1e5bcb8857f2c, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["limit"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["limit"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["limit"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["limit"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_a592af01d1baaf91e422593362f99f92_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_a592af01d1baaf91e422593362f99f92_79b11725;
})();

export const Debounceinput_debounceinput_9d1c74cba2b5ba0969e49ca7e4d2916f_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_9d1c74cba2b5ba0969e49ca7e4d2916f_79b11725 = memo(({children, ...rest}) => {
    const on_change_34d6f5298dd161a4ac394cdd4ebde1d4 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "max_per_artist", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_34d6f5298dd161a4ac394cdd4ebde1d4, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_per_artist"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_per_artist"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_per_artist"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_per_artist"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_9d1c74cba2b5ba0969e49ca7e4d2916f_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_9d1c74cba2b5ba0969e49ca7e4d2916f_79b11725;
})();

export const Debounceinput_debounceinput_fc728e7f5fa9a5004757b2c7c2706205_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_fc728e7f5fa9a5004757b2c7c2706205_79b11725 = memo(({children, ...rest}) => {
    const on_change_20a19edc8384e8deaf15ccdb0ddc49c7 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "min_plays", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_20a19edc8384e8deaf15ccdb0ddc49c7, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_plays"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_plays"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_plays"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_plays"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_fc728e7f5fa9a5004757b2c7c2706205_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_fc728e7f5fa9a5004757b2c7c2706205_79b11725;
})();

export const Debounceinput_debounceinput_b5a77c2b6ee59c11f878b69988ae69e3_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_b5a77c2b6ee59c11f878b69988ae69e3_79b11725 = memo(({children, ...rest}) => {
    const on_change_83ed9f68b0316d8c732bc22539b3f9b9 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "max_plays", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_83ed9f68b0316d8c732bc22539b3f9b9, placeholder:"", value:(isNotNullOrUndefined((isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_plays"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_plays"] : "")) ? (isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_plays"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["max_plays"] : "") : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_b5a77c2b6ee59c11f878b69988ae69e3_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_b5a77c2b6ee59c11f878b69988ae69e3_79b11725;
})();

export const Selectroot_select__root_c2819b2d0c9e1125ce5ced1c2f47d4dc_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_c2819b2d0c9e1125ce5ced1c2f47d4dc_79b11725 = memo(({children, ...rest}) => {
    const on_change_25a3d9882a5ffb7f741885fcb8c06dc4 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_filter", ({ ["key"] : "min_rating", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_25a3d9882a5ffb7f741885fcb8c06dc4, value:(isTrue(reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_rating"]) ? reflex___state____state__musicmind_ui___state___ui.filters_rx_state_?.["min_rating"] : "") }))},children)
    )
});
Selectroot_select__root_c2819b2d0c9e1125ce5ced1c2f47d4dc_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_c2819b2d0c9e1125ce5ced1c2f47d4dc_79b11725;
})();

export const Checkbox_checkbox_2027a5d734c9e1e61d06831e5a14bbad_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_2027a5d734c9e1e61d06831e5a14bbad_79b11725 = memo(({children, ...rest}) => {
    const on_change_4914d243febc27f602b70f7959ae39d0 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_unplayed", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ checked:reflex___state____state__musicmind_ui___state___ui.unplayed_rx_state_, onCheckedChange:on_change_4914d243febc27f602b70f7959ae39d0, size:"2" }))},)
    )
});
Checkbox_checkbox_2027a5d734c9e1e61d06831e5a14bbad_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_2027a5d734c9e1e61d06831e5a14bbad_79b11725;
})();

export const Cond_comp_872ac97654d44b1ed40fa4f504615be3_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_872ac97654d44b1ed40fa4f504615be3_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.filter_section_rx_state_?.valueOf?.() === "Limits"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_872ac97654d44b1ed40fa4f504615be3_79b11725.displayName = "Cond";
return Cond_comp_872ac97654d44b1ed40fa4f504615be3_79b11725;
})();

export const Debounceinput_debounceinput_ba13a5fb1c9c11f1f137405a1692c3fc_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_ba13a5fb1c9c11f1f137405a1692c3fc_79b11725 = memo(({children, ...rest}) => {
    const on_change_f6fc8e297959f8d48d6e1c82e1c7a366 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_based_on_query", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_f6fc8e297959f8d48d6e1c82e1c7a366, placeholder:"Search tracks or artists\u2026", value:(isNotNullOrUndefined(reflex___state____state__musicmind_ui___state___ui.based_on_query_rx_state_) ? reflex___state____state__musicmind_ui___state___ui.based_on_query_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_ba13a5fb1c9c11f1f137405a1692c3fc_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_ba13a5fb1c9c11f1f137405a1692c3fc_79b11725;
})();

export const Button_button_17f554894594064affef06f488a2e75e_79b11725 = /*#__PURE__*/ (() => {
const Button_button_17f554894594064affef06f488a2e75e_79b11725 = memo(({children, ...rest}) => {
    const on_click_3ff0cd3feaa45bfddb1ac01377dfaade = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.search_seed", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_3ff0cd3feaa45bfddb1ac01377dfaade }))},children)
    )
});
Button_button_17f554894594064affef06f488a2e75e_79b11725.displayName = "Button";
return Button_button_17f554894594064affef06f488a2e75e_79b11725;
})();

export const Foreach_comp_8f8fef83867cb89b67634eb28f734dc7_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_8f8fef83867cb89b67634eb28f734dc7_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.suggestions_rx_state_ ?? [],((item_rx_state_,index_d040e79306831378398a6f5dc1bc1709)=>(jsx(RadixThemesButton,{css:({ ["width"] : "100%" }),key:index_d040e79306831378398a6f5dc1bc1709,onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_seed", ({ ["seed"] : item_rx_state_ }), ({  })))], [_e], ({  })))),variant:"ghost"},item_rx_state_?.["label"]))))
    )
});
Foreach_comp_8f8fef83867cb89b67634eb28f734dc7_79b11725.displayName = "Foreach";
return Foreach_comp_8f8fef83867cb89b67634eb28f734dc7_79b11725;
})();

export const Debounceinput_debounceinput_81892dc7e487c181dc46b22670fc4315_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_81892dc7e487c181dc46b22670fc4315_79b11725 = memo(({children, ...rest}) => {
    const on_change_10a79caed88cfe319e5cd13d9bbf34dd = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_on_this_day", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_10a79caed88cfe319e5cd13d9bbf34dd, type:"date", value:(isNotNullOrUndefined(reflex___state____state__musicmind_ui___state___ui.on_this_day_rx_state_) ? reflex___state____state__musicmind_ui___state___ui.on_this_day_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_81892dc7e487c181dc46b22670fc4315_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_81892dc7e487c181dc46b22670fc4315_79b11725;
})();

export const Button_button_f025aae7c185a673f33aff45f8b066f5_79b11725 = /*#__PURE__*/ (() => {
const Button_button_f025aae7c185a673f33aff45f8b066f5_79b11725 = memo(({children, ...rest}) => {
    const on_click_e69d1d1bc89a19f138c2f69326e8e91a = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.find_on_this_day", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_e69d1d1bc89a19f138c2f69326e8e91a }))},children)
    )
});
Button_button_f025aae7c185a673f33aff45f8b066f5_79b11725.displayName = "Button";
return Button_button_f025aae7c185a673f33aff45f8b066f5_79b11725;
})();

export const Bare_comp_1ae5839bd25eeeffa1062b4412a82a46_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_1ae5839bd25eeeffa1062b4412a82a46_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.show_all_playlists_rx_state_ ? "Show fewer" : "Show all")
    )
});
Bare_comp_1ae5839bd25eeeffa1062b4412a82a46_79b11725.displayName = "Bare";
return Bare_comp_1ae5839bd25eeeffa1062b4412a82a46_79b11725;
})();

export const Button_button_fa6ec908e548f2da1916f0c6f4e0cbb4_79b11725 = /*#__PURE__*/ (() => {
const Button_button_fa6ec908e548f2da1916f0c6f4e0cbb4_79b11725 = memo(({children, ...rest}) => {
    const on_click_08784295c47db52c5b15219a0db63fbd = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.toggle_all_playlists", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ className:"home-playlist-toggle", onClick:on_click_08784295c47db52c5b15219a0db63fbd, variant:"ghost" }))},children)
    )
});
Button_button_fa6ec908e548f2da1916f0c6f4e0cbb4_79b11725.displayName = "Button";
return Button_button_fa6ec908e548f2da1916f0c6f4e0cbb4_79b11725;
})();

export const Cond_comp_de4fcd483192c3bc0bb5b68207761740_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_de4fcd483192c3bc0bb5b68207761740_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.playlists_rx_state_.length > 6)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_de4fcd483192c3bc0bb5b68207761740_79b11725.displayName = "Cond";
return Cond_comp_de4fcd483192c3bc0bb5b68207761740_79b11725;
})();

export const Bare_comp_cdc46c6548d9e60f82d9a1f55f07402a_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_cdc46c6548d9e60f82d9a1f55f07402a_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.playlists_rx_state_.length
    )
});
Bare_comp_cdc46c6548d9e60f82d9a1f55f07402a_79b11725.displayName = "Bare";
return Bare_comp_cdc46c6548d9e60f82d9a1f55f07402a_79b11725;
})();

export const Foreach_comp_8736b8c53a0ba61ee5e120c143b49bce_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_8736b8c53a0ba61ee5e120c143b49bce_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.visible_playlists_rx_state_ ?? [],((item_rx_state_,index_247a2c5897e2389b39efb410276668e0)=>(jsx(RadixThemesFlex,{align:"start",className:"rx-Stack playlist-row",direction:"row",justify:"between",key:index_247a2c5897e2389b39efb410276668e0,gap:"3"},jsx(RadixThemesLink,{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},jsx(ReactRouterLink,{target:(true ? "_blank" : ""),to:item_rx_state_?.["url"]},item_rx_state_?.["title"])),jsx(RadixThemesText,{as:"p",className:"home-playlist-size"},(JSON.stringify(item_rx_state_?.["trackCount"])))))))
    )
});
Foreach_comp_8736b8c53a0ba61ee5e120c143b49bce_79b11725.displayName = "Foreach";
return Foreach_comp_8736b8c53a0ba61ee5e120c143b49bce_79b11725;
})();

export const Bare_comp_65e526b328c06abbb3a42fffa634dff2_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_65e526b328c06abbb3a42fffa634dff2_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (JSON.stringify(reflex___state____state__musicmind_ui___state___ui.tracks_rx_state_.length))
    )
});
Bare_comp_65e526b328c06abbb3a42fffa634dff2_79b11725.displayName = "Bare";
return Bare_comp_65e526b328c06abbb3a42fffa634dff2_79b11725;
})();

export const Foreach_comp_f25a228430909c2ecb9e83e8b784881f_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_f25a228430909c2ecb9e83e8b784881f_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.tags_rx_state_ ?? [],((tag_rx_state_,index_fdf4bbf2e8e806e567902fe455e169d5)=>(jsx(RadixThemesBadge,{key:index_fdf4bbf2e8e806e567902fe455e169d5},tag_rx_state_))))
    )
});
Foreach_comp_f25a228430909c2ecb9e83e8b784881f_79b11725.displayName = "Foreach";
return Foreach_comp_f25a228430909c2ecb9e83e8b784881f_79b11725;
})();

export const Foreach_comp_f5e0c409524a56e742be4a0b59386693_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_f5e0c409524a56e742be4a0b59386693_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.tracks_rx_state_ ?? [],((track_rx_state_,index_374b4ad1fd4e2756df7be8a4127fac0e)=>(jsx(RadixThemesFlex,{align:"start",className:"rx-Stack track-row",direction:"row",justify:"between",key:index_374b4ad1fd4e2756df7be8a4127fac0e,gap:"3"},jsx(RadixThemesBox,{},jsx(RadixThemesText,{as:"p",className:"track-artist"},track_rx_state_?.["artist"]),jsx(RadixThemesText,{as:"p",className:"track-title"},track_rx_state_?.["title"])),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack track-facts",direction:"row",gap:"3"},jsx(Fragment,{},(!(((isTrue(track_rx_state_?.["bpm"]) ? track_rx_state_?.["bpm"] : null)?.valueOf?.() === null?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"track-bpm"},(JSON.stringify((isTrue(track_rx_state_?.["bpm"]) ? track_rx_state_?.["bpm"] : null)))," BPM"))):(jsx(Fragment,{},)))),jsx(RadixThemesText,{as:"p",className:"track-meta"},(isTrue(track_rx_state_?.["year"]) ? track_rx_state_?.["year"] : "")))))))
    )
});
Foreach_comp_f5e0c409524a56e742be4a0b59386693_79b11725.displayName = "Foreach";
return Foreach_comp_f5e0c409524a56e742be4a0b59386693_79b11725;
})();

export const Debounceinput_debounceinput_844af692326def292b9d53ee9260748c_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_844af692326def292b9d53ee9260748c_79b11725 = memo(({children, ...rest}) => {
    const on_change_cd90514f58996a9136b59df52ec3f9c7 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_playlist_name", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_cd90514f58996a9136b59df52ec3f9c7, placeholder:"Playlist name", value:(isNotNullOrUndefined(reflex___state____state__musicmind_ui___state___ui.playlist_name_rx_state_) ? reflex___state____state__musicmind_ui___state___ui.playlist_name_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_844af692326def292b9d53ee9260748c_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_844af692326def292b9d53ee9260748c_79b11725;
})();

export const Button_button_049ec7cb92a7f51859f1028742ac12c8_79b11725 = /*#__PURE__*/ (() => {
const Button_button_049ec7cb92a7f51859f1028742ac12c8_79b11725 = memo(({children, ...rest}) => {
    const on_click_3d71b141a284d665a99f0c67f03bb64c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.create_playlist", ({  }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:reflex___state____state__musicmind_ui___state___ui.busy_rx_state_, onClick:on_click_3d71b141a284d665a99f0c67f03bb64c }))},children)
    )
});
Button_button_049ec7cb92a7f51859f1028742ac12c8_79b11725.displayName = "Button";
return Button_button_049ec7cb92a7f51859f1028742ac12c8_79b11725;
})();

export const Cond_comp_fb42f0017a30b6c0f1294ccd9cf0ad5f_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_fb42f0017a30b6c0f1294ccd9cf0ad5f_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.tracks_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_fb42f0017a30b6c0f1294ccd9cf0ad5f_79b11725.displayName = "Cond";
return Cond_comp_fb42f0017a30b6c0f1294ccd9cf0ad5f_79b11725;
})();

export const Cond_comp_f89ec8ce21643be72fce36f9c88027da_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_f89ec8ce21643be72fce36f9c88027da_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.has_searched_rx_state_?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_f89ec8ce21643be72fce36f9c88027da_79b11725.displayName = "Cond";
return Cond_comp_f89ec8ce21643be72fce36f9c88027da_79b11725;
})();

export const Foreach_comp_f654aa0ee9a8df224884e9db9f44dc49_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_f654aa0ee9a8df224884e9db9f44dc49_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.missing_rx_state_ ?? [],((item_rx_state_,index_e5b6cd5e73d6fb6fe13d231e8a39a884)=>(jsx(RadixThemesText,{as:"p",key:index_e5b6cd5e73d6fb6fe13d231e8a39a884},item_rx_state_?.["artist"]," \u2014 ",item_rx_state_?.["title"]))))
    )
});
Foreach_comp_f654aa0ee9a8df224884e9db9f44dc49_79b11725.displayName = "Foreach";
return Foreach_comp_f654aa0ee9a8df224884e9db9f44dc49_79b11725;
})();

export const Cond_comp_79dabb39216830673f0f78472e53234c_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_79dabb39216830673f0f78472e53234c_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.missing_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_79dabb39216830673f0f78472e53234c_79b11725.displayName = "Cond";
return Cond_comp_79dabb39216830673f0f78472e53234c_79b11725;
})();

export const Bare_comp_95ed86fff23b278bc77abb583c461e10_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_95ed86fff23b278bc77abb583c461e10_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (isTrue(reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["tracks"]) ? reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["tracks"] : "0")
    )
});
Bare_comp_95ed86fff23b278bc77abb583c461e10_79b11725.displayName = "Bare";
return Bare_comp_95ed86fff23b278bc77abb583c461e10_79b11725;
})();

export const Bare_comp_3ffc36c393f78c11307ff9d7fdd2da61_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_3ffc36c393f78c11307ff9d7fdd2da61_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (isTrue(reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["artists"]) ? reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["artists"] : "0")
    )
});
Bare_comp_3ffc36c393f78c11307ff9d7fdd2da61_79b11725.displayName = "Bare";
return Bare_comp_3ffc36c393f78c11307ff9d7fdd2da61_79b11725;
})();

export const Bare_comp_a52ab8cfe08158d8678783db6940ffd5_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_a52ab8cfe08158d8678783db6940ffd5_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (isTrue(reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["plays"]) ? reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["plays"] : "0")
    )
});
Bare_comp_a52ab8cfe08158d8678783db6940ffd5_79b11725.displayName = "Bare";
return Bare_comp_a52ab8cfe08158d8678783db6940ffd5_79b11725;
})();

export const Bare_comp_d3498128910efbc3529b2b34ea9768db_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_d3498128910efbc3529b2b34ea9768db_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (isTrue(reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["playlists"]) ? reflex___state____state__musicmind_ui___state___ui.home_stats_display_rx_state_?.["playlists"] : "0")
    )
});
Bare_comp_d3498128910efbc3529b2b34ea9768db_79b11725.displayName = "Bare";
return Bare_comp_d3498128910efbc3529b2b34ea9768db_79b11725;
})();

export const Box_box_80e80832376f74e6e83cad1ab00c9b8c_79b11725 = /*#__PURE__*/ (() => {
const Box_box_80e80832376f74e6e83cad1ab00c9b8c_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesBox,{...mergeSlotProps(rest, ({ className:(() => { switch (JSON.stringify(reflex___state____state__musicmind_ui___state___ui.theme_rx_state_)) {case JSON.stringify("midnight"):  return ("app-shell theme-midnight");  break;case JSON.stringify("parchment"):  return ("app-shell theme-parchment");  break;case JSON.stringify("ocean"):  return ("app-shell theme-ocean");  break;case JSON.stringify("forest"):  return ("app-shell theme-forest");  break;default:  return ("app-shell");  break;};})() }))},children)
    )
});
Box_box_80e80832376f74e6e83cad1ab00c9b8c_79b11725.displayName = "Box";
return Box_box_80e80832376f74e6e83cad1ab00c9b8c_79b11725;
})();

export const Bare_comp_7132ba7e6107523cf1454c8a2ddf5942_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_7132ba7e6107523cf1454c8a2ddf5942_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.stats_display_rx_state_?.["total_tracks"]
    )
});
Bare_comp_7132ba7e6107523cf1454c8a2ddf5942_79b11725.displayName = "Bare";
return Bare_comp_7132ba7e6107523cf1454c8a2ddf5942_79b11725;
})();

export const Bare_comp_724d74d057f1c32419e73930ff069da6_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_724d74d057f1c32419e73930ff069da6_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.stats_display_rx_state_?.["total_artists"]
    )
});
Bare_comp_724d74d057f1c32419e73930ff069da6_79b11725.displayName = "Bare";
return Bare_comp_724d74d057f1c32419e73930ff069da6_79b11725;
})();

export const Bare_comp_142c267716429517e5a61c0ea7c3a3ec_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_142c267716429517e5a61c0ea7c3a3ec_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.stats_display_rx_state_?.["total_scrobbles"]
    )
});
Bare_comp_142c267716429517e5a61c0ea7c3a3ec_79b11725.displayName = "Bare";
return Bare_comp_142c267716429517e5a61c0ea7c3a3ec_79b11725;
})();

export const Bare_comp_6445d6329ba4fb655c5c840ec5b7b1dc_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_6445d6329ba4fb655c5c840ec5b7b1dc_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.stats_display_rx_state_?.["total_instrumental"]
    )
});
Bare_comp_6445d6329ba4fb655c5c840ec5b7b1dc_79b11725.displayName = "Bare";
return Bare_comp_6445d6329ba4fb655c5c840ec5b7b1dc_79b11725;
})();

export const Bare_comp_294b40b31e84239267f9b48ff75717db_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_294b40b31e84239267f9b48ff75717db_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.listening_granularity_rx_state_?.valueOf?.() === "month"?.valueOf?.()) ? "Scrobbles by month" : "Scrobbles by year")
    )
});
Bare_comp_294b40b31e84239267f9b48ff75717db_79b11725.displayName = "Bare";
return Bare_comp_294b40b31e84239267f9b48ff75717db_79b11725;
})();

export const Responsivecontainer_responsivecontainer_fb721bdc49c31d430fd170b16e9b4992_79b11725 = /*#__PURE__*/ (() => {
const Responsivecontainer_responsivecontainer_fb721bdc49c31d430fd170b16e9b4992_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RechartsResponsiveContainer,{...mergeSlotProps(rest, ({ height:300, minHeight:10, minWidth:10, width:"100%" }))},jsx(RechartsLineChart,{data:((reflex___state____state__musicmind_ui___state___ui.listening_granularity_rx_state_?.valueOf?.() === "month"?.valueOf?.()) ? reflex___state____state__musicmind_ui___state___ui.listening_by_month_rx_state_ : reflex___state____state__musicmind_ui___state___ui.listening_by_year_rx_state_),height:"100%",margin:({ ["top"] : 12, ["right"] : 18, ["bottom"] : 4, ["left"] : -18 }),width:"100%"},jsx(RechartsCartesianGrid,{stroke:"#e8e4db",vertical:false},),jsx(RechartsXAxis,{axisLine:false,dataKey:reflex___state____state__musicmind_ui___state___ui.listening_granularity_rx_state_,stroke:"var(--gray-9)",tickLine:false},),jsx(RechartsYAxis,{axisLine:false,stroke:"var(--gray-9)",tickLine:false},),jsx(RechartsTooltip,{contentStyle:({ ["background"] : "var(--gray-1)", ["borderColor"] : "var(--gray-4)", ["borderRadius"] : "8px" }),cursor:({ ["strokeWidth"] : 1, ["fill"] : "var(--gray-3)" }),itemStyle:({ ["color"] : "var(--gray-12)" }),labelStyle:({ ["color"] : "var(--gray-11)" })},),jsx(RechartsLine,{activeDot:({ ["stroke"] : "var(--accent-2)", ["fill"] : "var(--accent-10)" }),animationDuration:900,dataKey:"plays",dot:true,isAnimationActive:true,stroke:"#80532f",strokeWidth:3,type:"monotone"},)))
    )
});
Responsivecontainer_responsivecontainer_fb721bdc49c31d430fd170b16e9b4992_79b11725.displayName = "ResponsiveContainer";
return Responsivecontainer_responsivecontainer_fb721bdc49c31d430fd170b16e9b4992_79b11725;
})();

export const Cond_comp_d8f98078827772ece0732ca8812a11a4_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_d8f98078827772ece0732ca8812a11a4_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.listening_by_year_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_d8f98078827772ece0732ca8812a11a4_79b11725.displayName = "Cond";
return Cond_comp_d8f98078827772ece0732ca8812a11a4_79b11725;
})();

export const Selectroot_select__root_1a27634946209578a1994278f599868b_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_1a27634946209578a1994278f599868b_79b11725 = memo(({children, ...rest}) => {
    const on_change_2c9f201017a3920dcd2b8c830d8f3dd3 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_stats_limit", ({ ["kind"] : "artist", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ "aria-label":"Number of artist results", className:"stats-limit", onValueChange:on_change_2c9f201017a3920dcd2b8c830d8f3dd3, value:reflex___state____state__musicmind_ui___state___ui.artist_limit_rx_state_ }))},children)
    )
});
Selectroot_select__root_1a27634946209578a1994278f599868b_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_1a27634946209578a1994278f599868b_79b11725;
})();

export const Responsivecontainer_responsivecontainer_db123a50feede7a550fa790e51e731ad_79b11725 = /*#__PURE__*/ (() => {
const Responsivecontainer_responsivecontainer_db123a50feede7a550fa790e51e731ad_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RechartsResponsiveContainer,{...mergeSlotProps(rest, ({ height:320, minHeight:10, minWidth:10, width:"100%" }))},jsx(RechartsBarChart,{data:reflex___state____state__musicmind_ui___state___ui.top_artists_rx_state_,height:"100%",layout:"vertical",margin:({ ["top"] : 8, ["right"] : 18, ["bottom"] : 8, ["left"] : 6 }),width:"100%"},jsx(RechartsCartesianGrid,{horizontal:false,stroke:"#ebe6dd"},),jsx(RechartsXAxis,{axisLine:false,stroke:"var(--gray-9)",tickLine:false,type:"number"},),jsx(RechartsYAxis,{axisLine:false,dataKey:"artist",stroke:"var(--gray-9)",tickLine:false,type:"category",width:135},),jsx(RechartsTooltip,{contentStyle:({ ["background"] : "var(--gray-1)", ["borderColor"] : "var(--gray-4)", ["borderRadius"] : "8px" }),cursor:({ ["strokeWidth"] : 1, ["fill"] : "var(--gray-3)" }),itemStyle:({ ["color"] : "var(--gray-12)" }),labelStyle:({ ["color"] : "var(--gray-11)" })},),jsx(RechartsBar,{animationDuration:900,dataKey:"plays",fill:"#80532f",isAnimationActive:true,radius:[0, 6, 6, 0]},)))
    )
});
Responsivecontainer_responsivecontainer_db123a50feede7a550fa790e51e731ad_79b11725.displayName = "ResponsiveContainer";
return Responsivecontainer_responsivecontainer_db123a50feede7a550fa790e51e731ad_79b11725;
})();

export const Cond_comp_e0f4ca2576f7e5ae9483e0fcb9059fe1_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_e0f4ca2576f7e5ae9483e0fcb9059fe1_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.top_artists_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_e0f4ca2576f7e5ae9483e0fcb9059fe1_79b11725.displayName = "Cond";
return Cond_comp_e0f4ca2576f7e5ae9483e0fcb9059fe1_79b11725;
})();

export const Selectroot_select__root_65d9589fc54b3d3441fe120984dfb858_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_65d9589fc54b3d3441fe120984dfb858_79b11725 = memo(({children, ...rest}) => {
    const on_change_d79897817df5120ce454b5eaaef74c74 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_stats_limit", ({ ["kind"] : "country", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ "aria-label":"Number of country results", className:"stats-limit", onValueChange:on_change_d79897817df5120ce454b5eaaef74c74, value:reflex___state____state__musicmind_ui___state___ui.country_limit_rx_state_ }))},children)
    )
});
Selectroot_select__root_65d9589fc54b3d3441fe120984dfb858_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_65d9589fc54b3d3441fe120984dfb858_79b11725;
})();

export const Responsivecontainer_responsivecontainer_dc20308b724e0b39cebe35d62cd28369_79b11725 = /*#__PURE__*/ (() => {
const Responsivecontainer_responsivecontainer_dc20308b724e0b39cebe35d62cd28369_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RechartsResponsiveContainer,{...mergeSlotProps(rest, ({ height:320, minHeight:10, minWidth:10, width:"100%" }))},jsx(RechartsBarChart,{data:reflex___state____state__musicmind_ui___state___ui.by_country_rx_state_,height:"100%",layout:"vertical",margin:({ ["top"] : 8, ["right"] : 18, ["bottom"] : 8, ["left"] : 6 }),width:"100%"},jsx(RechartsCartesianGrid,{horizontal:false,stroke:"#ebe6dd"},),jsx(RechartsXAxis,{axisLine:false,stroke:"var(--gray-9)",tickLine:false,type:"number"},),jsx(RechartsYAxis,{axisLine:false,dataKey:"country",stroke:"var(--gray-9)",tickLine:false,type:"category",width:135},),jsx(RechartsTooltip,{contentStyle:({ ["background"] : "var(--gray-1)", ["borderColor"] : "var(--gray-4)", ["borderRadius"] : "8px" }),cursor:({ ["strokeWidth"] : 1, ["fill"] : "var(--gray-3)" }),itemStyle:({ ["color"] : "var(--gray-12)" }),labelStyle:({ ["color"] : "var(--gray-11)" })},),jsx(RechartsBar,{animationDuration:900,dataKey:"cnt",fill:"#567264",isAnimationActive:true,radius:[0, 6, 6, 0]},)))
    )
});
Responsivecontainer_responsivecontainer_dc20308b724e0b39cebe35d62cd28369_79b11725.displayName = "ResponsiveContainer";
return Responsivecontainer_responsivecontainer_dc20308b724e0b39cebe35d62cd28369_79b11725;
})();

export const Cond_comp_e7e3075c4968ce169a2d31dddfe098c9_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_e7e3075c4968ce169a2d31dddfe098c9_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.by_country_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_e7e3075c4968ce169a2d31dddfe098c9_79b11725.displayName = "Cond";
return Cond_comp_e7e3075c4968ce169a2d31dddfe098c9_79b11725;
})();

export const Bare_comp_b12e457dce865e16e91157f854851e46_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_b12e457dce865e16e91157f854851e46_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.genre_source_rx_state_?.valueOf?.() === "plex"?.valueOf?.()) ? "Genres from Plex library metadata" : "Enriched tags across your tracks")
    )
});
Bare_comp_b12e457dce865e16e91157f854851e46_79b11725.displayName = "Bare";
return Bare_comp_b12e457dce865e16e91157f854851e46_79b11725;
})();

export const Selectroot_select__root_edf2382559723a3c16bbf7dd52dbfb27_79b11725 = /*#__PURE__*/ (() => {
const Selectroot_select__root_edf2382559723a3c16bbf7dd52dbfb27_79b11725 = memo(({children, ...rest}) => {
    const on_change_ef27b402d601598fac2ed975bf1387a6 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_stats_limit", ({ ["kind"] : "genre", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ "aria-label":"Number of genre results", className:"stats-limit", onValueChange:on_change_ef27b402d601598fac2ed975bf1387a6, value:reflex___state____state__musicmind_ui___state___ui.genre_limit_rx_state_ }))},children)
    )
});
Selectroot_select__root_edf2382559723a3c16bbf7dd52dbfb27_79b11725.displayName = "SelectRoot";
return Selectroot_select__root_edf2382559723a3c16bbf7dd52dbfb27_79b11725;
})();

export const Responsivecontainer_responsivecontainer_fe4a4b1f489e1f73e623404c34e2b7a9_79b11725 = /*#__PURE__*/ (() => {
const Responsivecontainer_responsivecontainer_fe4a4b1f489e1f73e623404c34e2b7a9_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RechartsResponsiveContainer,{...mergeSlotProps(rest, ({ height:320, minHeight:10, minWidth:10, width:"100%" }))},jsx(RechartsBarChart,{data:reflex___state____state__musicmind_ui___state___ui.top_genres_rx_state_,height:"100%",layout:"vertical",margin:({ ["top"] : 8, ["right"] : 18, ["bottom"] : 8, ["left"] : 6 }),width:"100%"},jsx(RechartsCartesianGrid,{horizontal:false,stroke:"#ebe6dd"},),jsx(RechartsXAxis,{axisLine:false,stroke:"var(--gray-9)",tickLine:false,type:"number"},),jsx(RechartsYAxis,{axisLine:false,dataKey:"tag",stroke:"var(--gray-9)",tickLine:false,type:"category",width:135},),jsx(RechartsTooltip,{contentStyle:({ ["background"] : "var(--gray-1)", ["borderColor"] : "var(--gray-4)", ["borderRadius"] : "8px" }),cursor:({ ["strokeWidth"] : 1, ["fill"] : "var(--gray-3)" }),itemStyle:({ ["color"] : "var(--gray-12)" }),labelStyle:({ ["color"] : "var(--gray-11)" })},),jsx(RechartsBar,{animationDuration:900,dataKey:"cnt",fill:"#927082",isAnimationActive:true,radius:[0, 6, 6, 0]},)))
    )
});
Responsivecontainer_responsivecontainer_fe4a4b1f489e1f73e623404c34e2b7a9_79b11725.displayName = "ResponsiveContainer";
return Responsivecontainer_responsivecontainer_fe4a4b1f489e1f73e623404c34e2b7a9_79b11725;
})();

export const Cond_comp_eabaaa8e7866912cc18da2c52da9e2d6_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_eabaaa8e7866912cc18da2c52da9e2d6_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.top_genres_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_eabaaa8e7866912cc18da2c52da9e2d6_79b11725.displayName = "Cond";
return Cond_comp_eabaaa8e7866912cc18da2c52da9e2d6_79b11725;
})();

export const Responsivecontainer_responsivecontainer_712e1f240de8caa074f2755727a4711b_79b11725 = /*#__PURE__*/ (() => {
const Responsivecontainer_responsivecontainer_712e1f240de8caa074f2755727a4711b_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RechartsResponsiveContainer,{...mergeSlotProps(rest, ({ height:280, minHeight:10, minWidth:10, width:"100%" }))},jsx(RechartsBarChart,{data:reflex___state____state__musicmind_ui___state___ui.by_era_rx_state_,height:"100%",margin:({ ["top"] : 8, ["right"] : 12, ["bottom"] : 8, ["left"] : 4 }),width:"100%"},jsx(RechartsCartesianGrid,{stroke:"#ebe6dd",vertical:false},),jsx(RechartsXAxis,{axisLine:false,dataKey:"era",stroke:"var(--gray-9)",tickLine:false},),jsx(RechartsYAxis,{axisLine:false,stroke:"var(--gray-9)",tickLine:false},),jsx(RechartsTooltip,{contentStyle:({ ["background"] : "var(--gray-1)", ["borderColor"] : "var(--gray-4)", ["borderRadius"] : "8px" }),cursor:({ ["strokeWidth"] : 1, ["fill"] : "var(--gray-3)" }),itemStyle:({ ["color"] : "var(--gray-12)" }),labelStyle:({ ["color"] : "var(--gray-11)" })},),jsx(RechartsBar,{animationDuration:900,dataKey:"cnt",fill:"#b47b46",isAnimationActive:true,radius:[6, 6, 0, 0]},)))
    )
});
Responsivecontainer_responsivecontainer_712e1f240de8caa074f2755727a4711b_79b11725.displayName = "ResponsiveContainer";
return Responsivecontainer_responsivecontainer_712e1f240de8caa074f2755727a4711b_79b11725;
})();

export const Cond_comp_4faeda730b1370a111201c425546e096_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_4faeda730b1370a111201c425546e096_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.by_era_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_4faeda730b1370a111201c425546e096_79b11725.displayName = "Cond";
return Cond_comp_4faeda730b1370a111201c425546e096_79b11725;
})();

export const Responsivecontainer_responsivecontainer_67bb33d2c0b7cb7e7c31673ea29a96ec_79b11725 = /*#__PURE__*/ (() => {
const Responsivecontainer_responsivecontainer_67bb33d2c0b7cb7e7c31673ea29a96ec_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RechartsResponsiveContainer,{...mergeSlotProps(rest, ({ height:300, minHeight:10, minWidth:10, width:"100%" }))},jsx(RechartsPieChart,{className:"gender-chart",height:"100%",width:"100%"},jsx(RechartsTooltip,{contentStyle:({ ["background"] : "var(--gray-1)", ["borderColor"] : "var(--gray-4)", ["borderRadius"] : "8px" }),cursor:({ ["strokeWidth"] : 1, ["fill"] : "var(--gray-3)" }),itemStyle:({ ["color"] : "var(--gray-12)" }),labelStyle:({ ["color"] : "var(--gray-11)" })},),jsx(RechartsPie,{animationDuration:1000,cx:"50%",cy:"46%",data:reflex___state____state__musicmind_ui___state___ui.by_gender_rx_state_,dataKey:"cnt",fill:"var(--accent-3)",isAnimationActive:true,label:true,nameKey:"gender",outerRadius:88,stroke:"var(--accent-9)"},Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.by_gender_rx_state_ ?? [],((item_rx_state_,index_rx_state_)=>(jsx(RechartsCell,{fill:(() => { switch (JSON.stringify(index_rx_state_)) {case JSON.stringify(0):  return ("#80532f");  break;case JSON.stringify(1):  return ("#567264");  break;case JSON.stringify(2):  return ("#a56643");  break;default:  return ("#927082");  break;};})(),key:index_rx_state_},))))),jsx(RechartsLegend,{},)))
    )
});
Responsivecontainer_responsivecontainer_67bb33d2c0b7cb7e7c31673ea29a96ec_79b11725.displayName = "ResponsiveContainer";
return Responsivecontainer_responsivecontainer_67bb33d2c0b7cb7e7c31673ea29a96ec_79b11725;
})();

export const Cond_comp_208dd8fd06320774bc391d29e8527872_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_208dd8fd06320774bc391d29e8527872_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.by_gender_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_208dd8fd06320774bc391d29e8527872_79b11725.displayName = "Cond";
return Cond_comp_208dd8fd06320774bc391d29e8527872_79b11725;
})();

export const Button_button_da08d748b81222de191af16c73ff704f_79b11725 = /*#__PURE__*/ (() => {
const Button_button_da08d748b81222de191af16c73ff704f_79b11725 = memo(({children, ...rest}) => {
    const on_click_884e99b1703880b5da96e35e7cd00c7c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.scan_plex", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_884e99b1703880b5da96e35e7cd00c7c, variant:"outline" }))},children)
    )
});
Button_button_da08d748b81222de191af16c73ff704f_79b11725.displayName = "Button";
return Button_button_da08d748b81222de191af16c73ff704f_79b11725;
})();

export const Debounceinput_debounceinput_b7d0fb7a684774fbe1dde7b648c6b679_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_b7d0fb7a684774fbe1dde7b648c6b679_79b11725 = memo(({children, ...rest}) => {
    const ref_resync_artist = useRegisteredRef("ref_resync_artist");
const on_change_10588299d863f1e171d934cc6833bc64 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_resync_artist", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, id:"resync-artist", inputRef:ref_resync_artist, onChange:on_change_10588299d863f1e171d934cc6833bc64, placeholder:"Artist name", value:(isNotNullOrUndefined(reflex___state____state__musicmind_ui___state___ui.resync_artist_rx_state_) ? reflex___state____state__musicmind_ui___state___ui.resync_artist_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_b7d0fb7a684774fbe1dde7b648c6b679_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_b7d0fb7a684774fbe1dde7b648c6b679_79b11725;
})();

export const Debounceinput_debounceinput_312f092a56211ed0c1cde62b834231e5_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_312f092a56211ed0c1cde62b834231e5_79b11725 = memo(({children, ...rest}) => {
    const ref_resync_album = useRegisteredRef("ref_resync_album");
const on_change_981bd0776093c99a2d588d37ca8a5d70 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_resync_album", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, id:"resync-album", inputRef:ref_resync_album, onChange:on_change_981bd0776093c99a2d588d37ca8a5d70, placeholder:"Album title", value:(isNotNullOrUndefined(reflex___state____state__musicmind_ui___state___ui.resync_album_rx_state_) ? reflex___state____state__musicmind_ui___state___ui.resync_album_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_312f092a56211ed0c1cde62b834231e5_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_312f092a56211ed0c1cde62b834231e5_79b11725;
})();

export const Checkbox_checkbox_8c0e48ae178aa1fda9cc73efc7cdad2f_79b11725 = /*#__PURE__*/ (() => {
const Checkbox_checkbox_8c0e48ae178aa1fda9cc73efc7cdad2f_79b11725 = memo(({children, ...rest}) => {
    const on_change_d6c3869666d585a29f39799dfe5cb613 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_resync_apply", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesCheckbox,{...mergeSlotProps(rest, ({ checked:reflex___state____state__musicmind_ui___state___ui.resync_apply_rx_state_, onCheckedChange:on_change_d6c3869666d585a29f39799dfe5cb613, size:"2" }))},)
    )
});
Checkbox_checkbox_8c0e48ae178aa1fda9cc73efc7cdad2f_79b11725.displayName = "Checkbox";
return Checkbox_checkbox_8c0e48ae178aa1fda9cc73efc7cdad2f_79b11725;
})();

export const Bare_comp_00702baee8f831d1273773776735511e_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_00702baee8f831d1273773776735511e_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.resync_apply_rx_state_ ? "Refresh release" : "Preview changes")
    )
});
Bare_comp_00702baee8f831d1273773776735511e_79b11725.displayName = "Bare";
return Bare_comp_00702baee8f831d1273773776735511e_79b11725;
})();

export const Button_button_54fffa477e9dbc38888a5aeab3421b14_79b11725 = /*#__PURE__*/ (() => {
const Button_button_54fffa477e9dbc38888a5aeab3421b14_79b11725 = memo(({children, ...rest}) => {
    const on_click_457f1dc1f78582c04a82316b0db8d4d3 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_resync", ({  }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr((reflex___state____state__musicmind_ui___state___ui.resync_artist_rx_state_?.valueOf?.() === ""?.valueOf?.()), () => ((reflex___state____state__musicmind_ui___state___ui.resync_album_rx_state_?.valueOf?.() === ""?.valueOf?.()))), onClick:on_click_457f1dc1f78582c04a82316b0db8d4d3 }))},children)
    )
});
Button_button_54fffa477e9dbc38888a5aeab3421b14_79b11725.displayName = "Button";
return Button_button_54fffa477e9dbc38888a5aeab3421b14_79b11725;
})();

export const Cond_comp_7282f8cb61ce23729c2a825a227d3041_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_7282f8cb61ce23729c2a825a227d3041_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_7282f8cb61ce23729c2a825a227d3041_79b11725.displayName = "Cond";
return Cond_comp_7282f8cb61ce23729c2a825a227d3041_79b11725;
})();

export const Bare_comp_52e3f041e51ce7afdf5ba8a333ef1b82_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_52e3f041e51ce7afdf5ba8a333ef1b82_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.fullsync_phase_rx_state_
    )
});
Bare_comp_52e3f041e51ce7afdf5ba8a333ef1b82_79b11725.displayName = "Bare";
return Bare_comp_52e3f041e51ce7afdf5ba8a333ef1b82_79b11725;
})();

export const Progress_progress_39fd860ac430c28014fcc983f4cfbb3b_79b11725 = /*#__PURE__*/ (() => {
const Progress_progress_39fd860ac430c28014fcc983f4cfbb3b_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesProgress,{...mergeSlotProps(rest, ({ className:"fullsync-progress", css:({ ["width"] : "100%" }), max:100, size:"2", value:reflex___state____state__musicmind_ui___state___ui.fullsync_progress_rx_state_ }))},)
    )
});
Progress_progress_39fd860ac430c28014fcc983f4cfbb3b_79b11725.displayName = "Progress";
return Progress_progress_39fd860ac430c28014fcc983f4cfbb3b_79b11725;
})();

export const Bare_comp_48e44de59563bedf006a9b6124b04a0d_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_48e44de59563bedf006a9b6124b04a0d_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((JSON.stringify(reflex___state____state__musicmind_ui___state___ui.fullsync_step_rx_state_))+" of 12 stages")
    )
});
Bare_comp_48e44de59563bedf006a9b6124b04a0d_79b11725.displayName = "Bare";
return Bare_comp_48e44de59563bedf006a9b6124b04a0d_79b11725;
})();

export const Cond_comp_d0f1ba6540c106f8ace09e887e15b2ed_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_d0f1ba6540c106f8ace09e887e15b2ed_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("ingest"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fingerprint"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("copyforward"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("varesolve"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("recordingmbid"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("lastfm"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("mbenrich"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("aienrich"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("tagger"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_full"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_limited"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_library"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_analysis"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_maintenance")))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_d0f1ba6540c106f8ace09e887e15b2ed_79b11725.displayName = "Cond";
return Cond_comp_d0f1ba6540c106f8ace09e887e15b2ed_79b11725;
})();

export const Button_button_6ab587fc40be6a3efa7e578f9a20d5f3_79b11725 = /*#__PURE__*/ (() => {
const Button_button_6ab587fc40be6a3efa7e578f9a20d5f3_79b11725 = memo(({children, ...rest}) => {
    const on_click_4b492685c342ff63de6e8920fa7ca82d = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "fullsync" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"), () => (pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("ingest"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fingerprint"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("copyforward"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("varesolve"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("recordingmbid"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("lastfm"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("mbenrich"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("aienrich"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("tagger"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_full"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_limited"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_library"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_analysis"))), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_maintenance"))))), onClick:on_click_4b492685c342ff63de6e8920fa7ca82d }))},children)
    )
});
Button_button_6ab587fc40be6a3efa7e578f9a20d5f3_79b11725.displayName = "Button";
return Button_button_6ab587fc40be6a3efa7e578f9a20d5f3_79b11725;
})();

export const Button_button_cd71e316c69b04308d5fd582c2bdb2fd_79b11725 = /*#__PURE__*/ (() => {
const Button_button_cd71e316c69b04308d5fd582c2bdb2fd_79b11725 = memo(({children, ...rest}) => {
    const on_click_a3650319ffad9335bd1a3c207479dbb6 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "fullsync" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_a3650319ffad9335bd1a3c207479dbb6, variant:"outline" }))},children)
    )
});
Button_button_cd71e316c69b04308d5fd582c2bdb2fd_79b11725.displayName = "Button";
return Button_button_cd71e316c69b04308d5fd582c2bdb2fd_79b11725;
})();

export const Button_button_be64d8649281ecd4928f282311265654_79b11725 = /*#__PURE__*/ (() => {
const Button_button_be64d8649281ecd4928f282311265654_79b11725 = memo(({children, ...rest}) => {
    const on_click_167c8e2aa679e901ff096e962f07c5ab = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.stop_job", ({ ["name"] : "fullsync" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ color:"red", onClick:on_click_167c8e2aa679e901ff096e962f07c5ab }))},children)
    )
});
Button_button_be64d8649281ecd4928f282311265654_79b11725.displayName = "Button";
return Button_button_be64d8649281ecd4928f282311265654_79b11725;
})();

export const Cond_comp_a5060bfe4057a1e26ef0d64601e47af0_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_a5060bfe4057a1e26ef0d64601e47af0_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_full")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_a5060bfe4057a1e26ef0d64601e47af0_79b11725.displayName = "Cond";
return Cond_comp_a5060bfe4057a1e26ef0d64601e47af0_79b11725;
})();

export const Box_box_cb10dc42b7bf26b89e1f958ecdf1a384_79b11725 = /*#__PURE__*/ (() => {
const Box_box_cb10dc42b7bf26b89e1f958ecdf1a384_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesBox,{...mergeSlotProps(rest, ({ "aria-live":"polite", className:(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_full") ? "synapse-run-indicator is-running" : "synapse-run-indicator"), role:"status" }))},children)
    )
});
Box_box_cb10dc42b7bf26b89e1f958ecdf1a384_79b11725.displayName = "Box";
return Box_box_cb10dc42b7bf26b89e1f958ecdf1a384_79b11725;
})();

export const Bare_comp_ee2fe5a95aeefa47d06bcab31b8b11ee_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_ee2fe5a95aeefa47d06bcab31b8b11ee_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (JSON.stringify((isTrue(reflex___state____state__musicmind_ui___state___ui.synapse_rx_state_?.["analyzed"]) ? reflex___state____state__musicmind_ui___state___ui.synapse_rx_state_?.["analyzed"] : 0)))
    )
});
Bare_comp_ee2fe5a95aeefa47d06bcab31b8b11ee_79b11725.displayName = "Bare";
return Bare_comp_ee2fe5a95aeefa47d06bcab31b8b11ee_79b11725;
})();

export const Bare_comp_567b554ce9ecb657624a6376c95d7049_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_567b554ce9ecb657624a6376c95d7049_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (JSON.stringify((isTrue(reflex___state____state__musicmind_ui___state___ui.synapse_rx_state_?.["errors"]) ? reflex___state____state__musicmind_ui___state___ui.synapse_rx_state_?.["errors"] : 0)))
    )
});
Bare_comp_567b554ce9ecb657624a6376c95d7049_79b11725.displayName = "Bare";
return Bare_comp_567b554ce9ecb657624a6376c95d7049_79b11725;
})();

export const Button_button_044960c427d391e735354810b406ab67_79b11725 = /*#__PURE__*/ (() => {
const Button_button_044960c427d391e735354810b406ab67_79b11725 = memo(({children, ...rest}) => {
    const on_click_105ebeced3937d74c09e5069915a60c5 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "synapse_full" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_105ebeced3937d74c09e5069915a60c5 }))},children)
    )
});
Button_button_044960c427d391e735354810b406ab67_79b11725.displayName = "Button";
return Button_button_044960c427d391e735354810b406ab67_79b11725;
})();

export const Button_button_2ad0dc629ac00ea354749acad9c346c2_79b11725 = /*#__PURE__*/ (() => {
const Button_button_2ad0dc629ac00ea354749acad9c346c2_79b11725 = memo(({children, ...rest}) => {
    const on_click_be4952460a059a40e766fec2d43c1c01 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "synapse_count" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_be4952460a059a40e766fec2d43c1c01, variant:"outline" }))},children)
    )
});
Button_button_2ad0dc629ac00ea354749acad9c346c2_79b11725.displayName = "Button";
return Button_button_2ad0dc629ac00ea354749acad9c346c2_79b11725;
})();

export const Button_button_0656494f4e9bbe84396212937be2af2a_79b11725 = /*#__PURE__*/ (() => {
const Button_button_0656494f4e9bbe84396212937be2af2a_79b11725 = memo(({children, ...rest}) => {
    const on_click_633b373ddf1bfc2546c8f16b008e30a3 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "synapse_full" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_633b373ddf1bfc2546c8f16b008e30a3, variant:"outline" }))},children)
    )
});
Button_button_0656494f4e9bbe84396212937be2af2a_79b11725.displayName = "Button";
return Button_button_0656494f4e9bbe84396212937be2af2a_79b11725;
})();

export const Box_box_3ac9a7f578d3e0a889f44a71fed34dd5_79b11725 = /*#__PURE__*/ (() => {
const Box_box_3ac9a7f578d3e0a889f44a71fed34dd5_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesBox,{...mergeSlotProps(rest, ({ "aria-hidden":"true", className:(pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_full"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("synapse_limited"))) ? "synapse-neuron is-active" : "synapse-neuron") }))},children)
    )
});
Box_box_3ac9a7f578d3e0a889f44a71fed34dd5_79b11725.displayName = "Box";
return Box_box_3ac9a7f578d3e0a889f44a71fed34dd5_79b11725;
})();

export const Cond_comp_ec244e75bec82df45c36e2104ce2b0f8_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_ec244e75bec82df45c36e2104ce2b0f8_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_library")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_ec244e75bec82df45c36e2104ce2b0f8_79b11725.displayName = "Cond";
return Cond_comp_ec244e75bec82df45c36e2104ce2b0f8_79b11725;
})();

export const Button_button_4dfede3cef3ecd4e790b9ff772e982e2_79b11725 = /*#__PURE__*/ (() => {
const Button_button_4dfede3cef3ecd4e790b9ff772e982e2_79b11725 = memo(({children, ...rest}) => {
    const on_click_eb64cbcdf6450b35393d2293c901eff2 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "group_library" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_library"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_eb64cbcdf6450b35393d2293c901eff2 }))},children)
    )
});
Button_button_4dfede3cef3ecd4e790b9ff772e982e2_79b11725.displayName = "Button";
return Button_button_4dfede3cef3ecd4e790b9ff772e982e2_79b11725;
})();

export const Cond_comp_81dc29b47287aa9b69d87b0111ea57e2_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_81dc29b47287aa9b69d87b0111ea57e2_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("ingest")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_81dc29b47287aa9b69d87b0111ea57e2_79b11725.displayName = "Cond";
return Cond_comp_81dc29b47287aa9b69d87b0111ea57e2_79b11725;
})();

export const Button_button_2eeff3539d01d1c08296a425355260ba_79b11725 = /*#__PURE__*/ (() => {
const Button_button_2eeff3539d01d1c08296a425355260ba_79b11725 = memo(({children, ...rest}) => {
    const on_click_ecc86b0c7f4ab555ef4c8c17efe10d68 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "ingest" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_library"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_ecc86b0c7f4ab555ef4c8c17efe10d68 }))},children)
    )
});
Button_button_2eeff3539d01d1c08296a425355260ba_79b11725.displayName = "Button";
return Button_button_2eeff3539d01d1c08296a425355260ba_79b11725;
})();

export const Button_button_139d260d6e75b05b9647770798622b5a_79b11725 = /*#__PURE__*/ (() => {
const Button_button_139d260d6e75b05b9647770798622b5a_79b11725 = memo(({children, ...rest}) => {
    const on_click_8af647db612a094bff0bfbfb544f3c85 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "ingest" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_8af647db612a094bff0bfbfb544f3c85, variant:"outline" }))},children)
    )
});
Button_button_139d260d6e75b05b9647770798622b5a_79b11725.displayName = "Button";
return Button_button_139d260d6e75b05b9647770798622b5a_79b11725;
})();

export const Cond_comp_d4263cfcc0e763c98b63ccfb795a2696_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_d4263cfcc0e763c98b63ccfb795a2696_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("lastfm")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_d4263cfcc0e763c98b63ccfb795a2696_79b11725.displayName = "Cond";
return Cond_comp_d4263cfcc0e763c98b63ccfb795a2696_79b11725;
})();

export const Button_button_98fbe6862361ab67367a8188b63a2280_79b11725 = /*#__PURE__*/ (() => {
const Button_button_98fbe6862361ab67367a8188b63a2280_79b11725 = memo(({children, ...rest}) => {
    const on_click_e59e374533780de834200514cb1f3d11 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "lastfm" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_library"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_e59e374533780de834200514cb1f3d11 }))},children)
    )
});
Button_button_98fbe6862361ab67367a8188b63a2280_79b11725.displayName = "Button";
return Button_button_98fbe6862361ab67367a8188b63a2280_79b11725;
})();

export const Button_button_4e1059aa44f0b708e4a23f19bf4c8fcf_79b11725 = /*#__PURE__*/ (() => {
const Button_button_4e1059aa44f0b708e4a23f19bf4c8fcf_79b11725 = memo(({children, ...rest}) => {
    const on_click_5bff968aff5cbed17818b6d30c2fed64 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "lastfm" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_5bff968aff5cbed17818b6d30c2fed64, variant:"outline" }))},children)
    )
});
Button_button_4e1059aa44f0b708e4a23f19bf4c8fcf_79b11725.displayName = "Button";
return Button_button_4e1059aa44f0b708e4a23f19bf4c8fcf_79b11725;
})();

export const Cond_comp_a2a2130e02fdb4e2e619a40dc2b640c7_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_a2a2130e02fdb4e2e619a40dc2b640c7_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_a2a2130e02fdb4e2e619a40dc2b640c7_79b11725.displayName = "Cond";
return Cond_comp_a2a2130e02fdb4e2e619a40dc2b640c7_79b11725;
})();

export const Button_button_806cfcac200f6ec7e308111671c2429e_79b11725 = /*#__PURE__*/ (() => {
const Button_button_806cfcac200f6ec7e308111671c2429e_79b11725 = memo(({children, ...rest}) => {
    const on_click_8b2792854158ca8011a479683ec39536 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "group_enrichment" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_8b2792854158ca8011a479683ec39536 }))},children)
    )
});
Button_button_806cfcac200f6ec7e308111671c2429e_79b11725.displayName = "Button";
return Button_button_806cfcac200f6ec7e308111671c2429e_79b11725;
})();

export const Cond_comp_f4ffb8662ec69bafd07ca10a617690df_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_f4ffb8662ec69bafd07ca10a617690df_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("mbenrich")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_f4ffb8662ec69bafd07ca10a617690df_79b11725.displayName = "Cond";
return Cond_comp_f4ffb8662ec69bafd07ca10a617690df_79b11725;
})();

export const Button_button_293be505986e52952da82bff90d73160_79b11725 = /*#__PURE__*/ (() => {
const Button_button_293be505986e52952da82bff90d73160_79b11725 = memo(({children, ...rest}) => {
    const on_click_1f21163f60f603cf363f7a66a91e6941 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "mbenrich" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_1f21163f60f603cf363f7a66a91e6941 }))},children)
    )
});
Button_button_293be505986e52952da82bff90d73160_79b11725.displayName = "Button";
return Button_button_293be505986e52952da82bff90d73160_79b11725;
})();

export const Button_button_a4f6d4e5a5b8b40fe0023f64665e2f5c_79b11725 = /*#__PURE__*/ (() => {
const Button_button_a4f6d4e5a5b8b40fe0023f64665e2f5c_79b11725 = memo(({children, ...rest}) => {
    const on_click_a3d01c45627c699edba23cb9538edad1 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "mbenrich" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_a3d01c45627c699edba23cb9538edad1, variant:"outline" }))},children)
    )
});
Button_button_a4f6d4e5a5b8b40fe0023f64665e2f5c_79b11725.displayName = "Button";
return Button_button_a4f6d4e5a5b8b40fe0023f64665e2f5c_79b11725;
})();

export const Cond_comp_ff5c8b3a14f2f800654decb27e3b228f_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_ff5c8b3a14f2f800654decb27e3b228f_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("aienrich")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_ff5c8b3a14f2f800654decb27e3b228f_79b11725.displayName = "Cond";
return Cond_comp_ff5c8b3a14f2f800654decb27e3b228f_79b11725;
})();

export const Button_button_423ae876a6be253eca099c4427e2e916_79b11725 = /*#__PURE__*/ (() => {
const Button_button_423ae876a6be253eca099c4427e2e916_79b11725 = memo(({children, ...rest}) => {
    const on_click_fc3e07951cd66dfa587b780a6706be83 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "aienrich" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_fc3e07951cd66dfa587b780a6706be83 }))},children)
    )
});
Button_button_423ae876a6be253eca099c4427e2e916_79b11725.displayName = "Button";
return Button_button_423ae876a6be253eca099c4427e2e916_79b11725;
})();

export const Button_button_5cd9b2eedce0d712a00cec00d3e82c9e_79b11725 = /*#__PURE__*/ (() => {
const Button_button_5cd9b2eedce0d712a00cec00d3e82c9e_79b11725 = memo(({children, ...rest}) => {
    const on_click_b7ef56048b4d2a45dc79c3eaa71d1de9 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "aienrich" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_b7ef56048b4d2a45dc79c3eaa71d1de9, variant:"outline" }))},children)
    )
});
Button_button_5cd9b2eedce0d712a00cec00d3e82c9e_79b11725.displayName = "Button";
return Button_button_5cd9b2eedce0d712a00cec00d3e82c9e_79b11725;
})();

export const Cond_comp_67cd0b56040f482795ed8d718fa7456f_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_67cd0b56040f482795ed8d718fa7456f_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("tagger")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_67cd0b56040f482795ed8d718fa7456f_79b11725.displayName = "Cond";
return Cond_comp_67cd0b56040f482795ed8d718fa7456f_79b11725;
})();

export const Button_button_bfb052210cf0c28ed56e0a861afb528d_79b11725 = /*#__PURE__*/ (() => {
const Button_button_bfb052210cf0c28ed56e0a861afb528d_79b11725 = memo(({children, ...rest}) => {
    const on_click_2519afe44e424731676ab940ea34b85f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "tagger" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_2519afe44e424731676ab940ea34b85f }))},children)
    )
});
Button_button_bfb052210cf0c28ed56e0a861afb528d_79b11725.displayName = "Button";
return Button_button_bfb052210cf0c28ed56e0a861afb528d_79b11725;
})();

export const Button_button_596a97cd9aa2590a15dd464112610a80_79b11725 = /*#__PURE__*/ (() => {
const Button_button_596a97cd9aa2590a15dd464112610a80_79b11725 = memo(({children, ...rest}) => {
    const on_click_70e9154578a0f9e93d1dd4767e633c9c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "tagger" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_70e9154578a0f9e93d1dd4767e633c9c, variant:"outline" }))},children)
    )
});
Button_button_596a97cd9aa2590a15dd464112610a80_79b11725.displayName = "Button";
return Button_button_596a97cd9aa2590a15dd464112610a80_79b11725;
})();

export const Cond_comp_1dab34f959e3008c9db111c32760d3a2_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_1dab34f959e3008c9db111c32760d3a2_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("context")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_1dab34f959e3008c9db111c32760d3a2_79b11725.displayName = "Cond";
return Cond_comp_1dab34f959e3008c9db111c32760d3a2_79b11725;
})();

export const Button_button_9c06a658fd850fb43ab96ba0089980a0_79b11725 = /*#__PURE__*/ (() => {
const Button_button_9c06a658fd850fb43ab96ba0089980a0_79b11725 = memo(({children, ...rest}) => {
    const on_click_d7c181a89c00b0b405479d62de7f9ac7 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "context" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_d7c181a89c00b0b405479d62de7f9ac7 }))},children)
    )
});
Button_button_9c06a658fd850fb43ab96ba0089980a0_79b11725.displayName = "Button";
return Button_button_9c06a658fd850fb43ab96ba0089980a0_79b11725;
})();

export const Button_button_39e1f24e3b64f3dfd5ad8c8380a2e22d_79b11725 = /*#__PURE__*/ (() => {
const Button_button_39e1f24e3b64f3dfd5ad8c8380a2e22d_79b11725 = memo(({children, ...rest}) => {
    const on_click_07edcd46525b34bfe50f38cbbbad1aba = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "context" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_07edcd46525b34bfe50f38cbbbad1aba, variant:"outline" }))},children)
    )
});
Button_button_39e1f24e3b64f3dfd5ad8c8380a2e22d_79b11725.displayName = "Button";
return Button_button_39e1f24e3b64f3dfd5ad8c8380a2e22d_79b11725;
})();

export const Cond_comp_ba9d4adf1a228109120dff46051cf79b_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_ba9d4adf1a228109120dff46051cf79b_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("recordingmbid")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_ba9d4adf1a228109120dff46051cf79b_79b11725.displayName = "Cond";
return Cond_comp_ba9d4adf1a228109120dff46051cf79b_79b11725;
})();

export const Button_button_b678cce5a1a3f483f0b1c762b7e2bdaa_79b11725 = /*#__PURE__*/ (() => {
const Button_button_b678cce5a1a3f483f0b1c762b7e2bdaa_79b11725 = memo(({children, ...rest}) => {
    const on_click_79c86e5454eec545523d16d500e58fcb = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "recordingmbid" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_enrichment"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_79c86e5454eec545523d16d500e58fcb }))},children)
    )
});
Button_button_b678cce5a1a3f483f0b1c762b7e2bdaa_79b11725.displayName = "Button";
return Button_button_b678cce5a1a3f483f0b1c762b7e2bdaa_79b11725;
})();

export const Button_button_93b7136d879e4a4c84372f56de502785_79b11725 = /*#__PURE__*/ (() => {
const Button_button_93b7136d879e4a4c84372f56de502785_79b11725 = memo(({children, ...rest}) => {
    const on_click_5214757efdec7cff5e2916bf4bf6b2ef = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "recordingmbid" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_5214757efdec7cff5e2916bf4bf6b2ef, variant:"outline" }))},children)
    )
});
Button_button_93b7136d879e4a4c84372f56de502785_79b11725.displayName = "Button";
return Button_button_93b7136d879e4a4c84372f56de502785_79b11725;
})();

export const Cond_comp_f3f13fa9062db78a915f1b3cd2f15871_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_f3f13fa9062db78a915f1b3cd2f15871_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_analysis")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_f3f13fa9062db78a915f1b3cd2f15871_79b11725.displayName = "Cond";
return Cond_comp_f3f13fa9062db78a915f1b3cd2f15871_79b11725;
})();

export const Button_button_d18909122d6c569c944b19b4a69ab0e5_79b11725 = /*#__PURE__*/ (() => {
const Button_button_d18909122d6c569c944b19b4a69ab0e5_79b11725 = memo(({children, ...rest}) => {
    const on_click_ffa87ec2c91db197ab89e15b1f6546e9 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "group_analysis" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_analysis"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_ffa87ec2c91db197ab89e15b1f6546e9 }))},children)
    )
});
Button_button_d18909122d6c569c944b19b4a69ab0e5_79b11725.displayName = "Button";
return Button_button_d18909122d6c569c944b19b4a69ab0e5_79b11725;
})();

export const Cond_comp_001292865977e62b6fba52e932a9d697_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_001292865977e62b6fba52e932a9d697_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("gaps")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_001292865977e62b6fba52e932a9d697_79b11725.displayName = "Cond";
return Cond_comp_001292865977e62b6fba52e932a9d697_79b11725;
})();

export const Button_button_a075b065f9da4b9bde29e44797765929_79b11725 = /*#__PURE__*/ (() => {
const Button_button_a075b065f9da4b9bde29e44797765929_79b11725 = memo(({children, ...rest}) => {
    const on_click_8f929890e6147ce09094daa2b842ed9f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "gaps" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_analysis"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_8f929890e6147ce09094daa2b842ed9f }))},children)
    )
});
Button_button_a075b065f9da4b9bde29e44797765929_79b11725.displayName = "Button";
return Button_button_a075b065f9da4b9bde29e44797765929_79b11725;
})();

export const Button_button_bc8a5bcd3b73b11c2b420efe941cca53_79b11725 = /*#__PURE__*/ (() => {
const Button_button_bc8a5bcd3b73b11c2b420efe941cca53_79b11725 = memo(({children, ...rest}) => {
    const on_click_51d7de0411528b1be920bde71d984466 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "gaps" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_51d7de0411528b1be920bde71d984466, variant:"outline" }))},children)
    )
});
Button_button_bc8a5bcd3b73b11c2b420efe941cca53_79b11725.displayName = "Button";
return Button_button_bc8a5bcd3b73b11c2b420efe941cca53_79b11725;
})();

export const Cond_comp_09fc7c9455639279bb299ddd8badc101_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_09fc7c9455639279bb299ddd8badc101_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fingerprint")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_09fc7c9455639279bb299ddd8badc101_79b11725.displayName = "Cond";
return Cond_comp_09fc7c9455639279bb299ddd8badc101_79b11725;
})();

export const Button_button_412de5a99bfd48c65fdbbf7c4bc318f8_79b11725 = /*#__PURE__*/ (() => {
const Button_button_412de5a99bfd48c65fdbbf7c4bc318f8_79b11725 = memo(({children, ...rest}) => {
    const on_click_98ee4f9bdb6a84eac34a3ec866ed781c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "fingerprint" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_analysis"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_98ee4f9bdb6a84eac34a3ec866ed781c }))},children)
    )
});
Button_button_412de5a99bfd48c65fdbbf7c4bc318f8_79b11725.displayName = "Button";
return Button_button_412de5a99bfd48c65fdbbf7c4bc318f8_79b11725;
})();

export const Button_button_ff9dd3942ddd61a85c1e7896f19ee608_79b11725 = /*#__PURE__*/ (() => {
const Button_button_ff9dd3942ddd61a85c1e7896f19ee608_79b11725 = memo(({children, ...rest}) => {
    const on_click_6534eac1ae46c0b1671c3e622ff57526 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "fingerprint" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_6534eac1ae46c0b1671c3e622ff57526, variant:"outline" }))},children)
    )
});
Button_button_ff9dd3942ddd61a85c1e7896f19ee608_79b11725.displayName = "Button";
return Button_button_ff9dd3942ddd61a85c1e7896f19ee608_79b11725;
})();

export const Cond_comp_834e82f720c2b5bdefb6e75995dde666_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_834e82f720c2b5bdefb6e75995dde666_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("copyforward")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_834e82f720c2b5bdefb6e75995dde666_79b11725.displayName = "Cond";
return Cond_comp_834e82f720c2b5bdefb6e75995dde666_79b11725;
})();

export const Button_button_39be37f194505c41c972948ecf163d5a_79b11725 = /*#__PURE__*/ (() => {
const Button_button_39be37f194505c41c972948ecf163d5a_79b11725 = memo(({children, ...rest}) => {
    const on_click_fe4556dae486f4333e4c241d78572dff = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "copyforward" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_analysis"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_fe4556dae486f4333e4c241d78572dff }))},children)
    )
});
Button_button_39be37f194505c41c972948ecf163d5a_79b11725.displayName = "Button";
return Button_button_39be37f194505c41c972948ecf163d5a_79b11725;
})();

export const Button_button_55b8757adb7757a7b924cdbc3d59d461_79b11725 = /*#__PURE__*/ (() => {
const Button_button_55b8757adb7757a7b924cdbc3d59d461_79b11725 = memo(({children, ...rest}) => {
    const on_click_bd3bf7e987aa25b0177a55b7433686c9 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "copyforward" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_bd3bf7e987aa25b0177a55b7433686c9, variant:"outline" }))},children)
    )
});
Button_button_55b8757adb7757a7b924cdbc3d59d461_79b11725.displayName = "Button";
return Button_button_55b8757adb7757a7b924cdbc3d59d461_79b11725;
})();

export const Cond_comp_9ee34a47167922a3deb62764317774b3_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_9ee34a47167922a3deb62764317774b3_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_maintenance")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_9ee34a47167922a3deb62764317774b3_79b11725.displayName = "Cond";
return Cond_comp_9ee34a47167922a3deb62764317774b3_79b11725;
})();

export const Button_button_45a0687879b0417b1f8c49af4d4e491b_79b11725 = /*#__PURE__*/ (() => {
const Button_button_45a0687879b0417b1f8c49af4d4e491b_79b11725 = memo(({children, ...rest}) => {
    const on_click_00d750f8f79903f4e659735c3abd7f9a = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "group_maintenance" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_maintenance"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_00d750f8f79903f4e659735c3abd7f9a }))},children)
    )
});
Button_button_45a0687879b0417b1f8c49af4d4e491b_79b11725.displayName = "Button";
return Button_button_45a0687879b0417b1f8c49af4d4e491b_79b11725;
})();

export const Cond_comp_b2710c032ba1cb543616f7dbd10291bd_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_b2710c032ba1cb543616f7dbd10291bd_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("dedup")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_b2710c032ba1cb543616f7dbd10291bd_79b11725.displayName = "Cond";
return Cond_comp_b2710c032ba1cb543616f7dbd10291bd_79b11725;
})();

export const Button_button_edcadc2f4cb89d08397782ee3ed67949_79b11725 = /*#__PURE__*/ (() => {
const Button_button_edcadc2f4cb89d08397782ee3ed67949_79b11725 = memo(({children, ...rest}) => {
    const on_click_f4ae71fda9befe65f88a63832b1e3c6d = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "dedup" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_maintenance"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_f4ae71fda9befe65f88a63832b1e3c6d }))},children)
    )
});
Button_button_edcadc2f4cb89d08397782ee3ed67949_79b11725.displayName = "Button";
return Button_button_edcadc2f4cb89d08397782ee3ed67949_79b11725;
})();

export const Button_button_8a7ed816664d23d04d734eafe8b87d72_79b11725 = /*#__PURE__*/ (() => {
const Button_button_8a7ed816664d23d04d734eafe8b87d72_79b11725 = memo(({children, ...rest}) => {
    const on_click_f2d6dcc38e731e3d5dc7129d15b18dc0 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "dedup" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_f2d6dcc38e731e3d5dc7129d15b18dc0, variant:"outline" }))},children)
    )
});
Button_button_8a7ed816664d23d04d734eafe8b87d72_79b11725.displayName = "Button";
return Button_button_8a7ed816664d23d04d734eafe8b87d72_79b11725;
})();

export const Cond_comp_8a99e59e9cc40ad1ac8f8fd644b515d2_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_8a99e59e9cc40ad1ac8f8fd644b515d2_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("varesolve")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_8a99e59e9cc40ad1ac8f8fd644b515d2_79b11725.displayName = "Cond";
return Cond_comp_8a99e59e9cc40ad1ac8f8fd644b515d2_79b11725;
})();

export const Button_button_c1f211762e5cf1fc6b3d61d2db01601d_79b11725 = /*#__PURE__*/ (() => {
const Button_button_c1f211762e5cf1fc6b3d61d2db01601d_79b11725 = memo(({children, ...rest}) => {
    const on_click_f29e360b6dc3998b4d3e4481d5d80da4 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "varesolve" }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:pyOr(reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("group_maintenance"), () => (reflex___state____state__musicmind_ui___state___ui.running_jobs_rx_state_.includes("fullsync"))), onClick:on_click_f29e360b6dc3998b4d3e4481d5d80da4 }))},children)
    )
});
Button_button_c1f211762e5cf1fc6b3d61d2db01601d_79b11725.displayName = "Button";
return Button_button_c1f211762e5cf1fc6b3d61d2db01601d_79b11725;
})();

export const Button_button_8affb52ba4731f0a305a5c501508b3fc_79b11725 = /*#__PURE__*/ (() => {
const Button_button_8affb52ba4731f0a305a5c501508b3fc_79b11725 = memo(({children, ...rest}) => {
    const on_click_914c18c024adfc3e8d57ce1ad8581915 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_job", ({ ["name"] : "varesolve" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_914c18c024adfc3e8d57ce1ad8581915, variant:"outline" }))},children)
    )
});
Button_button_8affb52ba4731f0a305a5c501508b3fc_79b11725.displayName = "Button";
return Button_button_8affb52ba4731f0a305a5c501508b3fc_79b11725;
})();

export const Bare_comp_14cd4ff5ac2c7f386c16e993709219f9_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_14cd4ff5ac2c7f386c16e993709219f9_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.selected_job_label_rx_state_
    )
});
Bare_comp_14cd4ff5ac2c7f386c16e993709219f9_79b11725.displayName = "Bare";
return Bare_comp_14cd4ff5ac2c7f386c16e993709219f9_79b11725;
})();

export const Cond_comp_c50e0927991b64a4c91ffdfd4c69f7ff_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_c50e0927991b64a4c91ffdfd4c69f7ff_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.job_running_rx_state_?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_c50e0927991b64a4c91ffdfd4c69f7ff_79b11725.displayName = "Cond";
return Cond_comp_c50e0927991b64a4c91ffdfd4c69f7ff_79b11725;
})();

export const Button_button_f800acfbeeb0bdba508e05c483b89eae_79b11725 = /*#__PURE__*/ (() => {
const Button_button_f800acfbeeb0bdba508e05c483b89eae_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
const on_click_bfe73c6c9fdeb22ec3d77189dc07a07f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.stop_job", ({ ["name"] : reflex___state____state__musicmind_ui___state___ui.selected_job_rx_state_ }), ({  })))], [_e], ({  })))), [reflex___state____state__musicmind_ui___state___ui])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ color:"red", onClick:on_click_bfe73c6c9fdeb22ec3d77189dc07a07f }))},children)
    )
});
Button_button_f800acfbeeb0bdba508e05c483b89eae_79b11725.displayName = "Button";
return Button_button_f800acfbeeb0bdba508e05c483b89eae_79b11725;
})();

export const Button_button_e343c271fa9c1e052f62f0f3edd824e9_79b11725 = /*#__PURE__*/ (() => {
const Button_button_e343c271fa9c1e052f62f0f3edd824e9_79b11725 = memo(({children, ...rest}) => {
    const on_click_c33f1baefe7fb11ed110837851e43062 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.job_load", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_c33f1baefe7fb11ed110837851e43062, variant:"outline" }))},children)
    )
});
Button_button_e343c271fa9c1e052f62f0f3edd824e9_79b11725.displayName = "Button";
return Button_button_e343c271fa9c1e052f62f0f3edd824e9_79b11725;
})();

export const Button_button_73d58eac280b0aba66adcb9742d77eda_79b11725 = /*#__PURE__*/ (() => {
const Button_button_73d58eac280b0aba66adcb9742d77eda_79b11725 = memo(({children, ...rest}) => {
    const on_click_294c55400d5d584de6ce4c1f450cbdd8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_job_dialog_open", ({ ["is_open"] : false }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_294c55400d5d584de6ce4c1f450cbdd8, variant:"outline" }))},children)
    )
});
Button_button_73d58eac280b0aba66adcb9742d77eda_79b11725.displayName = "Button";
return Button_button_73d58eac280b0aba66adcb9742d77eda_79b11725;
})();

export const Cond_comp_3e8a7aaf13b515252843c7b4fd774ba6_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_3e8a7aaf13b515252843c7b4fd774ba6_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.selected_job_rx_state_?.valueOf?.() === "fullsync"?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_3e8a7aaf13b515252843c7b4fd774ba6_79b11725.displayName = "Cond";
return Cond_comp_3e8a7aaf13b515252843c7b4fd774ba6_79b11725;
})();

export const Bare_comp_c851ae3058c960c0e41e4d44b3021019_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_c851ae3058c960c0e41e4d44b3021019_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        reflex___state____state__musicmind_ui___state___ui.job_log_rx_state_
    )
});
Bare_comp_c851ae3058c960c0e41e4d44b3021019_79b11725.displayName = "Bare";
return Bare_comp_c851ae3058c960c0e41e4d44b3021019_79b11725;
})();

export const Dialogroot_dialog__root_fed71125069a26227aedbe769c243fdd_79b11725 = /*#__PURE__*/ (() => {
const Dialogroot_dialog__root_fed71125069a26227aedbe769c243fdd_79b11725 = memo(({children, ...rest}) => {
    const on_open_change_fc45153741d963dc4ae25c2101b42d32 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_job_dialog_open", ({ ["is_open"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesDialog.Root,{...mergeSlotProps(rest, ({ onOpenChange:on_open_change_fc45153741d963dc4ae25c2101b42d32, open:reflex___state____state__musicmind_ui___state___ui.job_dialog_open_rx_state_ }))},children)
    )
});
Dialogroot_dialog__root_fed71125069a26227aedbe769c243fdd_79b11725.displayName = "DialogRoot";
return Dialogroot_dialog__root_fed71125069a26227aedbe769c243fdd_79b11725;
})();

export const Button_button_178b08c19acefead71a208e185076782_79b11725 = /*#__PURE__*/ (() => {
const Button_button_178b08c19acefead71a208e185076782_79b11725 = memo(({children, ...rest}) => {
    const on_click_bde9e8bf3a9545ebc21990dcc484ba9c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.logs_load", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_bde9e8bf3a9545ebc21990dcc484ba9c }))},children)
    )
});
Button_button_178b08c19acefead71a208e185076782_79b11725.displayName = "Button";
return Button_button_178b08c19acefead71a208e185076782_79b11725;
})();

export const Foreach_comp_6e86ad6b85d604bc624d28548c8bba81_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_6e86ad6b85d604bc624d28548c8bba81_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.logs_rx_state_ ?? [],((entry_rx_state_,index_ac7adfc5c8e10cd658a8773d7e0d56ff)=>(jsx(RadixThemesBox,{className:"log-entry",key:index_ac7adfc5c8e10cd658a8773d7e0d56ff},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",direction:"row",justify:"between",gap:"3"},jsx(RadixThemesText,{as:"p"},entry_rx_state_?.["timestamp"]),jsx(RadixThemesText,{as:"p"},entry_rx_state_?.["prompt"]),jsx(RadixThemesBadge,{},(JSON.stringify(entry_rx_state_?.["count"])))),jsx(Fragment,{},(!((entry_rx_state_?.["error"]?.valueOf?.() === ""?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",css:({ ["color"] : "red" })},entry_rx_state_?.["error"]))):(jsx(Fragment,{},))))))))
    )
});
Foreach_comp_6e86ad6b85d604bc624d28548c8bba81_79b11725.displayName = "Foreach";
return Foreach_comp_6e86ad6b85d604bc624d28548c8bba81_79b11725;
})();

export const Debounceinput_debounceinput_2615f5a52740f8f248e817e45f36a5ce_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_2615f5a52740f8f248e817e45f36a5ce_79b11725 = memo(({children, ...rest}) => {
    const on_change_09aa011148f4255494af6e124d53b75f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_sql", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ css:({ ["width"] : "100%" }), debounceTimeout:300, element:RadixThemesTextArea, onChange:on_change_09aa011148f4255494af6e124d53b75f, value:reflex___state____state__musicmind_ui___state___ui.sql_rx_state_ }), "inputRef")},)
    )
});
Debounceinput_debounceinput_2615f5a52740f8f248e817e45f36a5ce_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_2615f5a52740f8f248e817e45f36a5ce_79b11725;
})();

export const Button_button_294597a4a01ef451475247826b3e9191_79b11725 = /*#__PURE__*/ (() => {
const Button_button_294597a4a01ef451475247826b3e9191_79b11725 = memo(({children, ...rest}) => {
    const on_click_ea4ecf0e8ef181d7cf573121efb54c91 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.run_query", ({  }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ disabled:reflex___state____state__musicmind_ui___state___ui.busy_rx_state_, onClick:on_click_ea4ecf0e8ef181d7cf573121efb54c91 }))},children)
    )
});
Button_button_294597a4a01ef451475247826b3e9191_79b11725.displayName = "Button";
return Button_button_294597a4a01ef451475247826b3e9191_79b11725;
})();

export const Foreach_comp_dcb31f49699894d79d4926442d59b467_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_dcb31f49699894d79d4926442d59b467_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.query_columns_rx_state_ ?? [],((col_rx_state_,index_fdf4bbf2e8e806e567902fe455e169d5)=>(jsx(RadixThemesBadge,{key:index_fdf4bbf2e8e806e567902fe455e169d5},col_rx_state_))))
    )
});
Foreach_comp_dcb31f49699894d79d4926442d59b467_79b11725.displayName = "Foreach";
return Foreach_comp_dcb31f49699894d79d4926442d59b467_79b11725;
})();

export const Foreach_comp_11f9f2ff5ceffa46e7e0d22f7c55d09e_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_11f9f2ff5ceffa46e7e0d22f7c55d09e_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.query_rows_rx_state_ ?? [],((row_rx_state_,index_095dfa7dea4599f2e53f05a2cf6974f7)=>(jsx(RadixThemesFlex,{align:"start",className:"rx-Stack query-row",direction:"row",key:index_095dfa7dea4599f2e53f05a2cf6974f7,gap:"3"},Array.prototype.map.call(row_rx_state_ ?? [],((cell_rx_state_,index_fdf4bbf2e8e806e567902fe455e169d5)=>(jsx(RadixThemesText,{as:"p",key:index_fdf4bbf2e8e806e567902fe455e169d5},cell_rx_state_))))))))
    )
});
Foreach_comp_11f9f2ff5ceffa46e7e0d22f7c55d09e_79b11725.displayName = "Foreach";
return Foreach_comp_11f9f2ff5ceffa46e7e0d22f7c55d09e_79b11725;
})();

export const Bare_comp_0caacae8b417a606d0496ba8285f6410_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_0caacae8b417a606d0496ba8285f6410_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((JSON.stringify(reflex___state____state__musicmind_ui___state___ui.gaps_rx_state_.length))+" missing artists")
    )
});
Bare_comp_0caacae8b417a606d0496ba8285f6410_79b11725.displayName = "Bare";
return Bare_comp_0caacae8b417a606d0496ba8285f6410_79b11725;
})();

export const Button_button_31bdb30b4a459dd7229d5dee8b6fbf2a_79b11725 = /*#__PURE__*/ (() => {
const Button_button_31bdb30b4a459dd7229d5dee8b6fbf2a_79b11725 = memo(({children, ...rest}) => {
    const on_click_132b1ad8d62a12bc734f3b3e0a5d9e8f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.gaps_load", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_132b1ad8d62a12bc734f3b3e0a5d9e8f, variant:"outline" }))},children)
    )
});
Button_button_31bdb30b4a459dd7229d5dee8b6fbf2a_79b11725.displayName = "Button";
return Button_button_31bdb30b4a459dd7229d5dee8b6fbf2a_79b11725;
})();

export const Foreach_comp_51dc22c9613563c30ef6ddedb3ce0b05_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_51dc22c9613563c30ef6ddedb3ce0b05_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.gap_buckets_rx_state_ ?? [],((bucket_rx_state_,index_8d40d365d73139a79f29bbb27649519e)=>(jsx("details",{className:"gap-category",key:index_8d40d365d73139a79f29bbb27649519e,open:(bucket_rx_state_?.["key"]?.valueOf?.() === "worth_acquiring"?.valueOf?.())},jsx("summary",{},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",direction:"row",justify:"between",gap:"3"},jsx(RadixThemesBox,{},jsx(RadixThemesHeading,{size:"4"},bucket_rx_state_?.["label"]),jsx(RadixThemesText,{as:"p",className:"gap-category-copy"},bucket_rx_state_?.["description"])),jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["gap"] : "3" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p"},((JSON.stringify(bucket_rx_state_?.["count"]))+" artists")),jsx(LucideChevronDown,{size:18},)))),jsx(Fragment,{},((bucket_rx_state_?.["count"] > 0)?(jsx(Fragment,{},jsx(RadixThemesBox,{className:"gap-artists"},Array.prototype.map.call(bucket_rx_state_?.["artists"] ?? [],((artist_rx_state_,index_e8aaa42390b3f0945172a7871b12f504)=>(jsx(RadixThemesFlex,{align:"start",className:"rx-Stack gap-artist-row",direction:"row",justify:"between",key:index_e8aaa42390b3f0945172a7871b12f504,gap:"3"},jsx(RadixThemesText,{as:"p"},artist_rx_state_?.["artist"]),jsx(RadixThemesText,{as:"p",className:"gap-play-count"},((JSON.stringify(artist_rx_state_?.["scrobbles"]))+" plays"))))))))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"gap-category-copy"},"No missing artists in this category.")))))))))
    )
});
Foreach_comp_51dc22c9613563c30ef6ddedb3ce0b05_79b11725.displayName = "Foreach";
return Foreach_comp_51dc22c9613563c30ef6ddedb3ce0b05_79b11725;
})();

export const Cond_comp_67df85267d18f7e8cdeeac209538aaef_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_67df85267d18f7e8cdeeac209538aaef_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((reflex___state____state__musicmind_ui___state___ui.gaps_rx_state_.length?.valueOf?.() === 0?.valueOf?.())?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_67df85267d18f7e8cdeeac209538aaef_79b11725.displayName = "Cond";
return Cond_comp_67df85267d18f7e8cdeeac209538aaef_79b11725;
})();

export const Debounceinput_debounceinput_2d82c506a8f5b4f93b32e235a9c76859_79b11725 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_2d82c506a8f5b4f93b32e235a9c76859_79b11725 = memo(({children, ...rest}) => {
    const on_change_12bf217db55a8666e14523853f5b1fff = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.set_playlist_key", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [])
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ debounceTimeout:300, element:RadixThemesTextField.Root, onChange:on_change_12bf217db55a8666e14523853f5b1fff, placeholder:"Playlist key", value:(isNotNullOrUndefined(reflex___state____state__musicmind_ui___state___ui.playlist_key_rx_state_) ? reflex___state____state__musicmind_ui___state___ui.playlist_key_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_2d82c506a8f5b4f93b32e235a9c76859_79b11725.displayName = "DebounceInput";
return Debounceinput_debounceinput_2d82c506a8f5b4f93b32e235a9c76859_79b11725;
})();

export const Button_button_86d885a1ca3fccb33b8f14fee870bf68_79b11725 = /*#__PURE__*/ (() => {
const Button_button_86d885a1ca3fccb33b8f14fee870bf68_79b11725 = memo(({children, ...rest}) => {
    const on_click_7c139aad633523387bdebec4ed95b9d8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.audit_load", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_7c139aad633523387bdebec4ed95b9d8 }))},children)
    )
});
Button_button_86d885a1ca3fccb33b8f14fee870bf68_79b11725.displayName = "Button";
return Button_button_86d885a1ca3fccb33b8f14fee870bf68_79b11725;
})();

export const Foreach_comp_7aea81b1b692f1e63e43dffa6ca9248a_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_7aea81b1b692f1e63e43dffa6ca9248a_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.playlists_rx_state_ ?? [],((p_rx_state_,index_7b305a8a0a137c3a6d363a754fa420e4)=>(jsx(RadixThemesButton,{className:"playlist-choice",key:index_7b305a8a0a137c3a6d363a754fa420e4,onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.select_playlist", ({ ["key"] : p_rx_state_?.["key"] }), ({  })))], [_e], ({  })))),variant:"outline"},p_rx_state_?.["title"]))))
    )
});
Foreach_comp_7aea81b1b692f1e63e43dffa6ca9248a_79b11725.displayName = "Foreach";
return Foreach_comp_7aea81b1b692f1e63e43dffa6ca9248a_79b11725;
})();

export const Bare_comp_2214076684929b5af5d6c83450424612_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_2214076684929b5af5d6c83450424612_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (isTrue(reflex___state____state__musicmind_ui___state___ui.audit_rx_state_?.["title"]) ? reflex___state____state__musicmind_ui___state___ui.audit_rx_state_?.["title"] : "")
    )
});
Bare_comp_2214076684929b5af5d6c83450424612_79b11725.displayName = "Bare";
return Bare_comp_2214076684929b5af5d6c83450424612_79b11725;
})();

export const Bare_comp_17c2be12a4e14ff10a88fdca9aa30cb2_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_17c2be12a4e14ff10a88fdca9aa30cb2_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (isTrue(reflex___state____state__musicmind_ui___state___ui.audit_rx_state_?.["summary"]) ? reflex___state____state__musicmind_ui___state___ui.audit_rx_state_?.["summary"] : "")
    )
});
Bare_comp_17c2be12a4e14ff10a88fdca9aa30cb2_79b11725.displayName = "Bare";
return Bare_comp_17c2be12a4e14ff10a88fdca9aa30cb2_79b11725;
})();

export const Cond_comp_387b3f250fd37b785615d5b267b7d658_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_387b3f250fd37b785615d5b267b7d658_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (isTrue((isTrue(reflex___state____state__musicmind_ui___state___ui.audit_rx_state_?.["summary"]) ? reflex___state____state__musicmind_ui___state___ui.audit_rx_state_?.["summary"] : ""))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_387b3f250fd37b785615d5b267b7d658_79b11725.displayName = "Cond";
return Cond_comp_387b3f250fd37b785615d5b267b7d658_79b11725;
})();

export const Bare_comp_db43fc098a6771d97cdf9d07b526a5f0_79b11725 = /*#__PURE__*/ (() => {
const Bare_comp_db43fc098a6771d97cdf9d07b526a5f0_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        ((JSON.stringify(reflex___state____state__musicmind_ui___state___ui.audit_tracks_rx_state_.length))+" tracks \u00b7 \u2014 means analysis is unavailable")
    )
});
Bare_comp_db43fc098a6771d97cdf9d07b526a5f0_79b11725.displayName = "Bare";
return Bare_comp_db43fc098a6771d97cdf9d07b526a5f0_79b11725;
})();

export const Foreach_comp_74083faa2f9d165f3b0ea0a77480630a_79b11725 = /*#__PURE__*/ (() => {
const Foreach_comp_74083faa2f9d165f3b0ea0a77480630a_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        Array.prototype.map.call(reflex___state____state__musicmind_ui___state___ui.audit_tracks_rx_state_ ?? [],((track_rx_state_,index_e533ad5ab28b32fab7c6d2579ac3d4a1)=>(jsx(RadixThemesTable.Row,{key:index_e533ad5ab28b32fab7c6d2579ac3d4a1},jsx(RadixThemesTable.Cell,{},track_rx_state_?.["number"]),jsx(RadixThemesTable.Cell,{},track_rx_state_?.["title"]),jsx(RadixThemesTable.Cell,{},track_rx_state_?.["artist"]),jsx(RadixThemesTable.Cell,{},track_rx_state_?.["bpm"]),jsx(RadixThemesTable.Cell,{},track_rx_state_?.["danceability"]),jsx(RadixThemesTable.Cell,{},track_rx_state_?.["voice"]),jsx(RadixThemesTable.Cell,{},track_rx_state_?.["verdict"])))))
    )
});
Foreach_comp_74083faa2f9d165f3b0ea0a77480630a_79b11725.displayName = "Foreach";
return Foreach_comp_74083faa2f9d165f3b0ea0a77480630a_79b11725;
})();

export const Cond_comp_2d4902817b4074a53617b8bcba17226d_79b11725 = /*#__PURE__*/ (() => {
const Cond_comp_2d4902817b4074a53617b8bcba17226d_79b11725 = memo(({children}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        (reflex___state____state__musicmind_ui___state___ui.audit_rx_state_.hasOwnProperty("title")?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_2d4902817b4074a53617b8bcba17226d_79b11725.displayName = "Cond";
return Cond_comp_2d4902817b4074a53617b8bcba17226d_79b11725;
})();

export const Button_button_e0f5d918198fc7d78ccbb7fa2c3d480b_79b11725 = /*#__PURE__*/ (() => {
const Button_button_e0f5d918198fc7d78ccbb7fa2c3d480b_79b11725 = memo(({children, ...rest}) => {
    const on_click_1f58e6a3518223dd11be6c09551edc52 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.update_load", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_1f58e6a3518223dd11be6c09551edc52 }))},children)
    )
});
Button_button_e0f5d918198fc7d78ccbb7fa2c3d480b_79b11725.displayName = "Button";
return Button_button_e0f5d918198fc7d78ccbb7fa2c3d480b_79b11725;
})();

export const Codeblock_prismasynclight_6cf5f671f342a08bb9c7413698aa92d4_79b11725 = /*#__PURE__*/ (() => {
const Codeblock_prismasynclight_6cf5f671f342a08bb9c7413698aa92d4_79b11725 = memo(({children, ...rest}) => {
    const { resolvedColorMode } = useContext(ColorModeContext)
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(SyntaxHighlighter,{...mergeSlotProps(rest, ({ children:(JSON.stringify(reflex___state____state__musicmind_ui___state___ui.update_info_rx_state_)), language:"json", style:((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.()) ? oneLight : oneDark) }))},)
    )
});
Codeblock_prismasynclight_6cf5f671f342a08bb9c7413698aa92d4_79b11725.displayName = "CodeBlock";
return Codeblock_prismasynclight_6cf5f671f342a08bb9c7413698aa92d4_79b11725;
})();

export const Button_button_cd60153317d7f87c2238d83836a59809_79b11725 = /*#__PURE__*/ (() => {
const Button_button_cd60153317d7f87c2238d83836a59809_79b11725 = memo(({children, ...rest}) => {
    const on_click_43985185ea8b8e67b3b4cc77235e8ffd = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "mb_dry_run" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_43985185ea8b8e67b3b4cc77235e8ffd }))},children)
    )
});
Button_button_cd60153317d7f87c2238d83836a59809_79b11725.displayName = "Button";
return Button_button_cd60153317d7f87c2238d83836a59809_79b11725;
})();

export const Button_button_900bc5195114151dfc9ac50e9e785f6a_79b11725 = /*#__PURE__*/ (() => {
const Button_button_900bc5195114151dfc9ac50e9e785f6a_79b11725 = memo(({children, ...rest}) => {
    const on_click_9aab695e04865261b0cff26f30aaa17a = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "mb_limited_run" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_9aab695e04865261b0cff26f30aaa17a }))},children)
    )
});
Button_button_900bc5195114151dfc9ac50e9e785f6a_79b11725.displayName = "Button";
return Button_button_900bc5195114151dfc9ac50e9e785f6a_79b11725;
})();

export const Button_button_196cd0965aef29e0d42a28249cfba730_79b11725 = /*#__PURE__*/ (() => {
const Button_button_196cd0965aef29e0d42a28249cfba730_79b11725 = memo(({children, ...rest}) => {
    const on_click_efdc3d6e1841ae5e9ef2f683048b9c97 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "ai_dry_run" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_efdc3d6e1841ae5e9ef2f683048b9c97 }))},children)
    )
});
Button_button_196cd0965aef29e0d42a28249cfba730_79b11725.displayName = "Button";
return Button_button_196cd0965aef29e0d42a28249cfba730_79b11725;
})();

export const Button_button_5101312dbed420d32b3e3d5755d8fa8c_79b11725 = /*#__PURE__*/ (() => {
const Button_button_5101312dbed420d32b3e3d5755d8fa8c_79b11725 = memo(({children, ...rest}) => {
    const on_click_bf930580bc00ba4a92d13eaeaa3b0c6c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.start_job", ({ ["name"] : "ai_limited_run" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_bf930580bc00ba4a92d13eaeaa3b0c6c }))},children)
    )
});
Button_button_5101312dbed420d32b3e3d5755d8fa8c_79b11725.displayName = "Button";
return Button_button_5101312dbed420d32b3e3d5755d8fa8c_79b11725;
})();

export const Button_button_9a585f94a117732837169a2f120808a5_79b11725 = /*#__PURE__*/ (() => {
const Button_button_9a585f94a117732837169a2f120808a5_79b11725 = memo(({children, ...rest}) => {
    const on_click_244d1cc95088062046cf166fb2ef2668 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.run_assertion", ({ ["key"] : "mbid_has_country" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_244d1cc95088062046cf166fb2ef2668 }))},children)
    )
});
Button_button_9a585f94a117732837169a2f120808a5_79b11725.displayName = "Button";
return Button_button_9a585f94a117732837169a2f120808a5_79b11725;
})();

export const Button_button_0f821b4279c79d93eae9ddb575f07612_79b11725 = /*#__PURE__*/ (() => {
const Button_button_0f821b4279c79d93eae9ddb575f07612_79b11725 = memo(({children, ...rest}) => {
    const on_click_2db763921bc6a7a4cea43cd7453bb29a = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.run_assertion", ({ ["key"] : "no_null_era" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_2db763921bc6a7a4cea43cd7453bb29a }))},children)
    )
});
Button_button_0f821b4279c79d93eae9ddb575f07612_79b11725.displayName = "Button";
return Button_button_0f821b4279c79d93eae9ddb575f07612_79b11725;
})();

export const Button_button_d24861037b0488d3f5984085bbf4bcf5_79b11725 = /*#__PURE__*/ (() => {
const Button_button_d24861037b0488d3f5984085bbf4bcf5_79b11725 = memo(({children, ...rest}) => {
    const on_click_58d5a7f018df7697e6cf59a230aefd31 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.run_assertion", ({ ["key"] : "unmatched_artists_not_in_meta" }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_58d5a7f018df7697e6cf59a230aefd31 }))},children)
    )
});
Button_button_d24861037b0488d3f5984085bbf4bcf5_79b11725.displayName = "Button";
return Button_button_d24861037b0488d3f5984085bbf4bcf5_79b11725;
})();

export const Codeblock_prismasynclight_e35bc225c4110a9d0c2a5ec2d6301118_79b11725 = /*#__PURE__*/ (() => {
const Codeblock_prismasynclight_e35bc225c4110a9d0c2a5ec2d6301118_79b11725 = memo(({children, ...rest}) => {
    const { resolvedColorMode } = useContext(ColorModeContext)
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(SyntaxHighlighter,{...mergeSlotProps(rest, ({ children:(JSON.stringify(reflex___state____state__musicmind_ui___state___ui.audit_rx_state_)), language:"json", style:((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.()) ? oneLight : oneDark) }))},)
    )
});
Codeblock_prismasynclight_e35bc225c4110a9d0c2a5ec2d6301118_79b11725.displayName = "CodeBlock";
return Codeblock_prismasynclight_e35bc225c4110a9d0c2a5ec2d6301118_79b11725;
})();

export const Button_button_db1737d3e73f6ec63a9635c7a55a877b_79b11725 = /*#__PURE__*/ (() => {
const Button_button_db1737d3e73f6ec63a9635c7a55a877b_79b11725 = memo(({children, ...rest}) => {
    const on_click_c33f1baefe7fb11ed110837851e43062 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.musicmind_ui___state___ui.job_load", ({  }), ({  })))], [_e], ({  })))), [])
    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ onClick:on_click_c33f1baefe7fb11ed110837851e43062 }))},children)
    )
});
Button_button_db1737d3e73f6ec63a9635c7a55a877b_79b11725.displayName = "Button";
return Button_button_db1737d3e73f6ec63a9635c7a55a877b_79b11725;
})();

export const Codeblock_prismasynclight_2c377f88a23acf8e33f244e85d564b40_79b11725 = /*#__PURE__*/ (() => {
const Codeblock_prismasynclight_2c377f88a23acf8e33f244e85d564b40_79b11725 = memo(({children, ...rest}) => {
    const { resolvedColorMode } = useContext(ColorModeContext)
const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(SyntaxHighlighter,{...mergeSlotProps(rest, ({ children:reflex___state____state__musicmind_ui___state___ui.job_log_rx_state_, language:"text", style:((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.()) ? oneLight : oneDark) }))},)
    )
});
Codeblock_prismasynclight_2c377f88a23acf8e33f244e85d564b40_79b11725.displayName = "CodeBlock";
return Codeblock_prismasynclight_2c377f88a23acf8e33f244e85d564b40_79b11725;
})();

export const Markdown_reactmarkdown_beb3b784e02e9449035adbd9be7a3a2d_79b11725 = /*#__PURE__*/ (() => {
const Markdown_reactmarkdown_beb3b784e02e9449035adbd9be7a3a2d_79b11725 = memo(({children, ...rest}) => {
    const reflex___state____state__musicmind_ui___state___ui = useStateContext("reflex___state____state.musicmind_ui___state___ui")
    return(
        jsx(ReactMarkdown,{...mergeSlotProps(rest, ({ components:ComponentMap_d8b2dcef1196f2645c614da09ad39de0(), rehypePlugins:[rehypeKatex, rehypeRaw, rehypeUnwrapImages], remarkPlugins:[remarkMath, remarkGfm] }))},reflex___state____state__musicmind_ui___state___ui.guide_text_rx_state_)
    )
});
Markdown_reactmarkdown_beb3b784e02e9449035adbd9be7a3a2d_79b11725.displayName = "Markdown";
return Markdown_reactmarkdown_beb3b784e02e9449035adbd9be7a3a2d_79b11725;
})();
