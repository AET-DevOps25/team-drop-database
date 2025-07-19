{{/*
--------------------------------------------------------------------------------
 Generic helpers – can be reused by any chart
--------------------------------------------------------------------------------
*/}}

{{/* Return the (optionally overridden) name, max 63 chars */}}
{{- define "common.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/* Return the full release-qualified name, max 63 chars */}}
{{- define "common.fullname" -}}
{{- $name := include "common.name" . -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end }}

{{/* Standard Kubernetes/Helm labels */}}
{{- define "common.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "common.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}


{{/*
--------------------------------------------------------------------------------
 Per‑micro‑service wrappers
 Each chart calls only its own wrapper name/fullname, which in turn delegates
 to the generic helpers above.  Add more wrappers here if you introduce new
 micro‑services later.
--------------------------------------------------------------------------------
*/}}

{{/* ───── frontend ───── */}}
{{- define "frontend.name" -}}
{{- include "common.name" . -}}
{{- end }}
{{- define "frontend.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{/* ───── authservice ───── */}}
{{- define "authservice.name" -}}
{{- include "common.name" . -}}
{{- end }}
{{- define "authservice.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{/* ───── userservice ───── */}}
{{- define "userservice.name" -}}
{{- include "common.name" . -}}
{{- end }}
{{- define "userservice.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{/* ───── attractionservice ───── */}}
{{- define "attractionservice.name" -}}
{{- include "common.name" . -}}
{{- end }}
{{- define "attractionservice.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{/* ───── ingress chart (travel‑buddy‑ingress) ───── */}}
{{- define "travel-buddy-ingress.name" -}}
{{- include "common.name" . -}}
{{- end }}
{{- define "travel-buddy-ingress.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}
