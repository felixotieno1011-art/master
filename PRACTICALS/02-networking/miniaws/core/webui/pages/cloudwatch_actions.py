"""CloudWatch form actions."""
import urllib.parse

from core import cloudwatch as cw


def _redirect(loc):
    return ("redirect", loc)


def _ok(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}ok={urllib.parse.quote(str(msg))}")


def _err(path, msg):
    sep = "&" if "?" in path else "?"
    return _redirect(f"{path}{sep}error={urllib.parse.quote(str(msg))}")


def handle(path, form, files=None):
    routes = {
        "/cloudwatch/alarms/create":   _create_alarm,
        "/cloudwatch/alarms/delete":   _delete_alarm,
        "/cloudwatch/alarms/evaluate": _evaluate_alarms,
        "/cloudwatch/log-groups/create": _create_log_group,
    }
    fn = routes.get(path)
    return fn(form) if fn else None


def _create_alarm(form):
    name = (form.get("name") or "").strip()
    ns = (form.get("namespace") or "").strip()
    metric = (form.get("metric_name") or form.get("metric") or "").strip()
    threshold = form.get("threshold") or "0"
    comparison = (form.get("comparison") or "GreaterThanThreshold").strip()
    statistic = (form.get("statistic") or "Average").strip()
    periods = form.get("periods") or "1"

    if not name or not ns or not metric:
        return _err("/cloudwatch/alarms/create", "name, namespace, and metric required")
    try:
        threshold_f = float(threshold)
    except ValueError:
        return _err("/cloudwatch/alarms/create", "threshold must be a number")
    try:
        periods_i = int(periods)
    except ValueError:
        periods_i = 1

    ok_, msg = cw.put_metric_alarm(
        name, ns, metric, threshold_f,
        comparison=comparison,
        evaluation_periods=periods_i,
        stat=statistic,
    )
    if not ok_:
        return _err("/cloudwatch/alarms/create", msg)
    return _ok("/cloudwatch/alarms", msg)


def _delete_alarm(form):
    name = (form.get("name") or "").strip()
    if not name:
        return _err("/cloudwatch/alarms", "name required")
    ok_, msg = cw.delete_alarm(name)
    return _ok("/cloudwatch/alarms", msg) if ok_ else _err("/cloudwatch/alarms", msg)


def _evaluate_alarms(form):
    try:
        cw.evaluate_alarms()
        return _ok("/cloudwatch/alarms", "evaluated all alarms")
    except Exception as e:
        return _err("/cloudwatch/alarms", str(e))


def _create_log_group(form):
    name = (form.get("name") or "").strip()
    if not name:
        return _err("/cloudwatch/log-groups/create", "name required")
    ok_, msg = cw.create_log_group(name)
    if not ok_:
        return _err("/cloudwatch/log-groups/create", msg)
    return _ok("/cloudwatch/log-groups", msg)
