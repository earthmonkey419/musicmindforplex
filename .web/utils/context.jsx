import React, { useContext, useMemo, useState, createElement, useEffect } from "react"
import { applyDelta, ReflexEvent, hydrateClientStorage, useEventLoop, refs } from "$/utils/state"
import { ColorModeContext, UploadFilesContext, DispatchContext, EventLoopContext, StateStoreContext, registerApp, eventLoop } from "$/utils/context-registry"
import { jsx } from "@emotion/react";

// Disable React dev-build owner-stack capture: the per-element Error()
// dominates dev-mode render CPU on large pages. Costs owner frames in
// `React.captureOwnerStack()`; set REFLEX_REACT_OWNER_STACKS=1 to restore.
// Full context: https://github.com/reflex-dev/reflex/pull/6905
if (typeof window !== "undefined") {
  try {
    const reactInternals =
      React.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;
    const ownerStackCounterKey = "recentlyCreatedOwnerStacks";
    if (
      reactInternals &&
      typeof reactInternals[ownerStackCounterKey] === "number"
    ) {
      Object.defineProperty(reactInternals, ownerStackCounterKey, {
        get: () => 1e9,
        set: () => {},
        configurable: true,
      });
    }
  } catch {}
}

export { ColorModeContext, UploadFilesContext, DispatchContext, EventLoopContext, StateStoreContext };
export const initialState = {"reflex___state____state": {"is_hydrated_rx_state_": false, "rx_router_headers_rx_state_": {"host": "", "origin": "", "upgrade": "", "connection": "", "pragma": "", "cache_control": "", "user_agent": "", "sec_websocket_version": "", "sec_websocket_key": "", "sec_websocket_extensions": "", "accept_encoding": "", "accept_language": "", "raw_headers": {}}, "rx_router_page_rx_state_": {"host": "", "path": "", "raw_path": "", "full_path": "", "full_raw_path": "", "params": {}}, "rx_router_route_id_rx_state_": "", "rx_router_session_rx_state_": {"client_token": "", "client_ip": "", "session_id": ""}, "rx_router_url_rx_state_": {"scheme": "", "netloc": "", "origin": "://", "path": "", "query": "", "query_parameters": {}, "fragment": "", "href": ""}}, "reflex___state____state.musicmind_ui___state___ui": {"artist_limit_rx_state_": "10", "audit_rx_state_": {}, "audit_tracks_rx_state_": [], "based_on_query_rx_state_": "", "buckets_rx_state_": [], "busy_rx_state_": false, "by_country_rx_state_": [], "by_era_rx_state_": [], "by_gender_rx_state_": [], "countries_rx_state_": [], "country_limit_rx_state_": "10", "country_names_rx_state_": [], "filter_section_rx_state_": "Sound", "filters_rx_state_": {"limit": "30", "max_per_artist": "1", "order": "BPM flow"}, "filters_open_rx_state_": false, "fullsync_phase_rx_state_": "Waiting to start", "fullsync_progress_rx_state_": 0, "fullsync_step_rx_state_": 0, "gap_buckets_rx_state_": [], "gaps_rx_state_": [], "genre_families_open_rx_state_": false, "genre_limit_rx_state_": "10", "genre_names_rx_state_": [], "genre_source_rx_state_": "tags", "genres_rx_state_": [], "guide_text_rx_state_": "", "has_searched_rx_state_": false, "home_stats_rx_state_": {"tracks": 0, "artists": 0, "plays": 0, "playlists": 0}, "home_stats_display_rx_state_": {"tracks": "0", "artists": "0", "plays": "0", "playlists": "0"}, "instrumental_rx_state_": false, "job_dialog_open_rx_state_": false, "job_log_rx_state_": "", "job_running_rx_state_": false, "listening_by_month_rx_state_": [], "listening_by_year_rx_state_": [], "listening_granularity_rx_state_": "year", "logs_rx_state_": [], "message_rx_state_": "", "missing_rx_state_": [], "on_this_day_rx_state_": "", "open_job_groups_rx_state_": [], "playlist_key_rx_state_": "", "playlist_name_rx_state_": "", "playlists_rx_state_": [], "plex_machine_id_rx_state_": "", "prompt_rx_state_": "", "query_columns_rx_state_": [], "query_rows_rx_state_": [], "resync_album_rx_state_": "", "resync_apply_rx_state_": false, "resync_artist_rx_state_": "", "running_jobs_rx_state_": [], "selected_job_rx_state_": "fullsync", "selected_job_label_rx_state_": "Full sync", "selected_seed_rx_state_": {}, "show_all_playlists_rx_state_": false, "sql_rx_state_": "SELECT * FROM tracks LIMIT 20", "stats_rx_state_": {}, "stats_display_rx_state_": {"total_tracks": "0", "total_artists": "0", "total_scrobbles": "0", "total_instrumental": "0"}, "stats_summary_rx_state_": {"total_tracks": 0, "total_artists": 0, "total_scrobbles": 0, "total_instrumental": 0}, "suggestions_rx_state_": [], "synapse_rx_state_": {}, "synapse_errors_rx_state_": [], "synapse_limit_rx_state_": "10", "tags_rx_state_": [], "theme_rx_state_": "light", "top_artists_rx_state_": [], "top_genres_rx_state_": [], "tracks_rx_state_": [], "unplayed_rx_state_": false, "update_info_rx_state_": {}, "visible_playlists_rx_state_": []}, "reflex___state____state.reflex___istate___shared____shared_state_base_internal": {}, "reflex___state____state.reflex___state____frontend_event_exception_state": {}, "reflex___state____state.reflex___state____on_load_internal_state": {}, "reflex___state____state.reflex___state____update_vars_internal_state": {}}
export const initialStateHashes = ["414f9a536fb1adf0", "d029e8db883816fc", "f53b93a5b661f0e9", "bf21a9e8fbc5a384", "bf21a9e8fbc5a384", "bf21a9e8fbc5a384", "bf21a9e8fbc5a384"]
export const stateSchema = "90625b980bee2e44488eab30c1f3329a"

export const defaultColorMode = "light"
export const clientStorage = {"cookies": {}, "local_storage": {}, "session_storage": {}}


export const state_name = "reflex___state____state"
export const on_load_internal_event = 'reflex___state____state.reflex___state____on_load_internal_state.on_load_internal'

export const exception_state_name = "reflex___state____state.reflex___state____frontend_event_exception_state"

// Tracked cookie and local storage vars set in the browser, or undefined if none.
const clientStorageVars = () => {
    const client_storage_vars = hydrateClientStorage(clientStorage);
    if (client_storage_vars && Object.keys(client_storage_vars).length !== 0) {
        return client_storage_vars;
    }
    return undefined;
}

// These events are triggered on each client-side page navigation.
export const onLoadInternalEvent = () => {
    const internal_events = [];

    // Only send the client storage vars if any are actually set in the browser.
    const client_storage_vars = clientStorageVars();
    if (client_storage_vars !== undefined) {
        internal_events.push(
            ReflexEvent(
                'reflex___state____state.reflex___state____update_vars_internal_state.update_vars_internal',
                {vars: client_storage_vars},
            ),
        );
    }

    // `on_load_internal` triggers the correct on_load event(s) for the current page.
    // If the page does not define any on_load event, this will just set `is_hydrated = true`.
    internal_events.push(ReflexEvent('reflex___state____state.reflex___state____on_load_internal_state.on_load_internal'));

    return internal_events;
}

// The single event sent when the websocket connects or reconnects: it resets and
// applies client storage, sends the state, and queues the page's on_load events.
// On the first connect the frontend still holds the compiled defaults, so it
// sends their hashes and the backend only returns the vars that differ; any
// later (re)hydrate gets the full state.
export const initialEvents = (first = false) => {
    const client_storage_vars = clientStorageVars();
    const payload = {};
    if (client_storage_vars !== undefined) {
        payload["vars"] = client_storage_vars;
    }
    if (first) {
        payload["hashes"] = initialStateHashes;
    }
    return [ReflexEvent('reflex___state____state.hydrate_and_load', payload)];
}
    

export const isDevMode = true;

// The static runtime reads these through the registry, so this module is the
// only one Vite re-executes when they change.
registerApp({
  initialState,
  clientStorage,
  state_name,
  on_load_internal_event,
  stateSchema,
  exception_state_name,
  onLoadInternalEvent,
  initialEvents,
  isDevMode,
  defaultColorMode,
});

export function addEvents(events, args, event_actions) {
  return eventLoop.addEvents(events, args, event_actions);
}

export function getConnectErrors() {
  return eventLoop.connectErrors;
}

export function UploadFilesProvider({ children }) {
  const [filesById, setFilesById] = useState({})
  // Serialized callbacks run outside components and read the current selection.
  refs["__upload_files"] = filesById;
  refs["__clear_selected_files"] = (id) => setFilesById(filesById => {
    const newFilesById = {...filesById}
    delete newFilesById[id]
    return newFilesById
  })
  return createElement(
    UploadFilesContext.Provider,
    { value: [filesById, setFilesById] },
    children
  );
}

// ``displayName`` is what React DevTools shows for the wrapper; without it
// every client-only component in the tree renders as ``Anonymous``.
export function ClientSide(component, name) {
  function ClientSideComponent({ children, ...props }) {
    const [Component, setComponent] = useState(null);
    useEffect(() => {
      async function load() {
        const comp = await component();
        setComponent(() => comp);
      }
      load();
    }, []);
    return Component ? jsx(Component, props, children) : null;
  }
  ClientSideComponent.displayName = name ? `ClientSide(${name})` : "ClientSide";
  return ClientSideComponent;
}

export function EventLoopProvider({ children }) {
  const dispatch = useContext(DispatchContext)
  const [addEventsLocal, connectErrors] = useEventLoop(
    dispatch,
    initialEvents,
    clientStorage,
  )
  // Publish the dispatchers so JSX literals constructed outside the
  // React-tree path (e.g. ``ErrorBoundary.onError``) can call ``addEvents``.
  eventLoop.addEvents = addEventsLocal;
  eventLoop.connectErrors = connectErrors;
  return useMemo(
    () =>
      createElement(
        EventLoopContext.Provider,
        { value: [addEventsLocal, connectErrors] },
        children
      ),
    [addEventsLocal, connectErrors, children],
  );
}

// Dispatch updates happen outside render; useSyncExternalStore keeps reads
// consistent while notifying only consumers of the changed substate.
function createStateStore(initialState) {
  const state = {};
  const listeners = new Map();
  const dispatchers = {};
  const notify = (substateName) =>
    listeners.get(substateName)?.forEach((listener) => listener());
  // Hot reload passes the recompiled initial state: new substates are added,
  // and existing substates gain new fields at their defaults while keeping
  // their live values.
  const mergeInitialState = (nextInitialState) => {
    for (const [substateName, value] of Object.entries(nextInitialState)) {
      const liveState = state[substateName];
      if (liveState !== undefined) {
        if (Object.keys(value).some((key) => !Object.hasOwn(liveState, key))) {
          state[substateName] = { ...value, ...liveState };
          notify(substateName);
        }
        continue;
      }
      state[substateName] = value;
      dispatchers[substateName] = (delta) => {
        const currentState = state[substateName];
        const nextState = applyDelta(currentState, delta);
        if (nextState === currentState) return;
        state[substateName] = nextState;
        notify(substateName);
      };
      notify(substateName);
    }
  };
  mergeInitialState(initialState);

  return {
    dispatchers,
    mergeInitialState,
    getSnapshot: (substateName) => state[substateName],
    subscribe: (substateName, listener) => {
      let substateListeners = listeners.get(substateName);
      if (!substateListeners) {
        substateListeners = new Set();
        listeners.set(substateName, substateListeners);
      }
      substateListeners.add(listener);
      return () => substateListeners.delete(listener);
    },
  };
}

function StateStoreProviders({ children, store }) {
  return createElement(
    StateStoreContext,
    { value: store },
    createElement(DispatchContext, { value: store.dispatchers }, children),
  );
}

function ClientStateProvider({ children }) {
  const [store] = useState(() => createStateStore(initialState));
  useEffect(() => store.mergeInitialState(initialState), [store, initialState]);
  return createElement(StateStoreProviders, { children, store });
}

// The server renders once and never applies a delta, so it only reads the
// initial state.
const serverStateStore = {
  dispatchers: {},
  getSnapshot: (substateName) => initialState[substateName],
  subscribe: () => () => {},
};

function ServerStateProvider({ children }) {
  return createElement(StateStoreProviders, { children, store: serverStateStore });
}

export const StateProvider =
  typeof document === "undefined" ? ServerStateProvider : ClientStateProvider;