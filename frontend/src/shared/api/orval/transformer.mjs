/**
 * Orval input transformer for the FastAPI spec.
 *
 * - Strips the /api/v1 prefix from paths — the axios instance's baseURL
 *   (see api.config.ts) already ends with /api/v1.
 * - Cleans FastAPI's auto-generated operationIds down to the route handler
 *   name: `sign_in_api_v1_auth_sign_in_post` -> `sign_in`.
 * - Handler names that collide across tags (e.g. `create_topic` in both
 *   Speaking and Writing) get prefixed with their tag, because operation
 *   names must be unique for the shared model/ output.
 *
 */

export const API_PREFIX = "/api/v1";
export const EXCLUDED_TAGS = ["Health", "Metrics", "Webhook"];

export const HTTP_METHODS = [
  "get",
  "post",
  "put",
  "patch",
  "delete",
  "head",
  "options",
  "trace",
];

export const stripApiPrefix = (path) =>
  path.startsWith(API_PREFIX) ? path.slice(API_PREFIX.length) : path;

/**
 * FastAPI builds operationIds as `re.sub(r"\W", "_", name + path) + "_" + method`.
 * Reconstruct that suffix from the path + method and strip it, leaving `name`.
 */
export const cleanOperationId = (operationId, path, method) => {
  const suffix = `${path.replace(/[^A-Za-z0-9_]/g, "_")}_${method.toLowerCase()}`;
  return operationId.endsWith(suffix)
    ? operationId.slice(0, -suffix.length)
    : operationId;
};

const tagToPrefix = (tag) => tag.toLowerCase().replace(/[^a-z0-9]+/g, "_");

/** Iterate [path, method, operation] triples of a spec */
export const eachOperation = (spec, fn) => {
  for (const [path, pathItem] of Object.entries(spec.paths ?? {})) {
    for (const [method, operation] of Object.entries(pathItem)) {
      if (HTTP_METHODS.includes(method) && typeof operation === "object") {
        fn(path, method, operation);
      }
    }
  }
};

const transformSpec = (spec) => {
  const nameCounts = new Map();

  eachOperation(spec, (path, method, operation) => {
    if (!operation.operationId) return;
    operation.operationId = cleanOperationId(operation.operationId, path, method);
    nameCounts.set(
      operation.operationId,
      (nameCounts.get(operation.operationId) ?? 0) + 1,
    );
  });

  eachOperation(spec, (_path, _method, operation) => {
    const tag = operation.tags?.[0];
    if (operation.operationId && nameCounts.get(operation.operationId) > 1 && tag) {
      operation.operationId = `${tagToPrefix(tag)}_${operation.operationId}`;
    }
  });

  return {
    ...spec,
    paths: Object.fromEntries(
      Object.entries(spec.paths ?? {}).map(([path, pathItem]) => [
        stripApiPrefix(path),
        pathItem,
      ]),
    ),
  };
};

export default transformSpec;
