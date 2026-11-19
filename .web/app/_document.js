import {Links,Meta,Scripts,ScrollRestoration} from "react-router"
import reflexGlobalStyles from "$/styles/__reflex_global_styles.css?url"
import {jsx} from "@emotion/react"
import {Fragment,useEffect} from "react"

export function Layout({children}) {
  return (
    jsx("html",{lang:"en",suppressHydrationWarning:true},jsx("head",{},jsx("script",{},"\n// Only run in browser environment, not during SSR\nif (typeof document !== 'undefined') {\n    try {\n        const theme = localStorage.getItem(\"theme\") || 'light';\n        const systemPreference = window.matchMedia(\"(prefers-color-scheme: dark)\").matches ? \"dark\" : \"light\";\n        const resolvedTheme = theme === \"system\" ? systemPreference : theme;\n\n        // Apply theme immediately - blocks until complete\n        // Use classList to avoid overwriting other classes\n        document.documentElement.classList.remove(\"light\", \"dark\");\n        document.documentElement.classList.add(resolvedTheme);\n        document.documentElement.style.colorScheme = resolvedTheme;\n\n    } catch (e) {\n        // Fallback to system preference on any error (resolve \"system\" to actual theme)\n        const fallbackTheme = window.matchMedia(\"(prefers-color-scheme: dark)\").matches ? \"dark\" : \"light\";\n        document.documentElement.classList.remove(\"light\", \"dark\");\n        document.documentElement.classList.add(fallbackTheme);\n        document.documentElement.style.colorScheme = fallbackTheme;\n    }\n}\n"),jsx("meta",{charSet:"utf-8"},),jsx("meta",{content:"width=device-width, initial-scale=1",name:"viewport"},),jsx(Meta,{},),jsx("link",{href:reflexGlobalStyles,rel:"stylesheet",type:"text/css"},),jsx(Links,{},)),jsx("body",{},children,jsx(ScrollRestoration,{},),jsx(Scripts,{},)))
  )
}