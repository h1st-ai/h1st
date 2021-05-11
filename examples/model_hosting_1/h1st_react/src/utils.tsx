/**
 * We want to get the base url in the format https://<domain>/<appname> on production
 */
export function getFullUrl(url: string) {
  const first_path_segment = window.location.pathname.split("/")[1];
  return `${new URL(
    first_path_segment,
    window.location.origin
  ).toString()}${url}`;
}
