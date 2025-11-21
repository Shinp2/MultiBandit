#!/usr/bin/env bash
# Compact wrapper for experiment_ar.py

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
if [ -f "$SCRIPT_DIR/experiment_ar.py" ]; then
	PY_SCRIPT="$SCRIPT_DIR/experiment_ar.py"
else
	echo "python script not found; looked for experiment_ar.py in script dir, ../python, and /home/shinp/programs/python" >&2
	exit 2
fi

usage(){
	cat <<-USAGE
Usage: $0 [--times X Y ...] [--times-file FILE] [--times-file-lines FILE] [--epsilons-file FILE] [--Ks K1 K2 ...] [--Ks-file FILE] [--Ks-file-lines FILE] [--theta-file FILE] [--theta-file-lines FILE] [--out TEMPLATE] [other args...]
If a *-file-lines option is used, the script will run once per non-empty line; use {n} in --out to inject line number.
USAGE
}

make_out_name(){
	local tmpl="$1" n="$2"
	if [[ "$tmpl" == *"{n}"* ]]; then
		printf '%s' "${tmpl//\{n\}/$n}"
		return
	fi
	local base="${tmpl%.*}" ext="${tmpl##*.}"
	if [[ "$base" == "$tmpl" ]]; then
		printf '%s' "${tmpl}_$n"
	else
		printf '%s' "${base}_$n.$ext"
	fi
}

run_once(){
	local times_args=("$@")
	local cmd=(python3 "$PY_SCRIPT" --times)
	for t in "${times_args[@]}"; do cmd+=("$t"); done
	for ea in "${EXTRA_ARGS[@]:-}"; do cmd+=("$ea"); done
	# measure elapsed time for the command
	local start end elapsed
	start=$(date +%s.%N)
	echo "Running: ${cmd[*]}"
	"${cmd[@]}"
	end=$(date +%s.%N)
	elapsed=$(awk -v e="$end" -v s="$start" 'BEGIN{printf "%.3f", e - s}')
	echo "Elapsed: ${elapsed}s"
}

run_eps_once(){
	local eps_args=("$@")
	local cmd=(python3 "$PY_SCRIPT" --epsilons)
	for e in "${eps_args[@]}"; do cmd+=("$e"); done
	for ea in "${EXTRA_ARGS[@]:-}"; do cmd+=("$ea"); done
	local start end elapsed
	start=$(date +%s.%N)
	echo "Running: ${cmd[*]}"
	"${cmd[@]}"
	end=$(date +%s.%N)
	elapsed=$(awk -v e="$end" -v s="$start" 'BEGIN{printf "%.3f", e - s}')
	echo "Elapsed: ${elapsed}s"
}

run_K_once(){
    local ks_args=("$@")
    local cmd=(python3 "$PY_SCRIPT" --Ks)
    for k in "${ks_args[@]}"; do cmd+=("$k"); done
    for ea in "${EXTRA_ARGS[@]:-}"; do cmd+=("$ea"); done
	local start end elapsed
	start=$(date +%s.%N)
	echo "Running: ${cmd[*]}"
	"${cmd[@]}"
	end=$(date +%s.%N)
	elapsed=$(awk -v e="$end" -v s="$start" 'BEGIN{printf "%.3f", e - s}')
	echo "Elapsed: ${elapsed}s"
}

run_generic(){
	# run python script with any EXTRA_ARGS, optional TIMES (if set),
	# and any additional args passed to this function (e.g. --theta vals)
	local extra_args=("${EXTRA_ARGS[@]:-}")
	local more_args=("$@")
	local cmd=(python3 "$PY_SCRIPT")
	if [[ ${#TIMES[@]} -gt 0 ]]; then
		cmd+=(--times)
		for t in "${TIMES[@]}"; do cmd+=("$t"); done
	fi
	for ea in "${extra_args[@]}"; do cmd+=("$ea"); done
	for a in "${more_args[@]}"; do cmd+=("$a"); done

	local start end elapsed
	start=$(date +%s.%N)
	echo "Running: ${cmd[*]}"
	"${cmd[@]}"
	end=$(date +%s.%N)
	elapsed=$(awk -v e="$end" -v s="$start" 'BEGIN{printf "%.3f", e - s}')
	echo "Elapsed: ${elapsed}s"
}

# Parse args
TIMES=()
TIMES_FILE=""
TIMES_FILE_LINES=""
OUT_TEMPLATE=""
EPS_FILE=""
EPS_FILE_LINES=""
KS=()
KS_FILE_LINES=""
KS_FILE=""
THETA_FILE=""
THETA_FILE_LINES=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
	case "$1" in
		--times)
			shift
			while [[ $# -gt 0 && ! "$1" == -* ]]; do
				# allow comma-separated or space-separated
				IFS=',' read -ra parts <<< "$1"
				for p in "${parts[@]}"; do
					for q in $p; do TIMES+=("$q"); done
				done
				shift
			done
			;;
		--times-file)
			TIMES_FILE="$2"; shift 2;;
		--times-file-lines)
			TIMES_FILE_LINES="$2"; shift 2;;
        --Ks-file)
            KS_FILE="$2"; shift 2;;
		--theta-file)
			THETA_FILE="$2"; shift 2;;
		--Ks)
			shift
			while [[ $# -gt 0 && ! "$1" == -* ]]; do
				IFS=',' read -ra parts <<< "$1"
				for p in "${parts[@]}"; do
					for q in $p; do KS+=("$q"); done
				done
				shift
			done
			;;
		--Ks-file-lines)
			KS_FILE_LINES="$2"; shift 2;;
		--theta-file-lines)
			THETA_FILE_LINES="$2"; shift 2;;
		--epsilons-file-lines)
			EPS_FILE_LINES="$2"; shift 2;;
		--epsilons-file)
			EPS_FILE="$2"; shift 2;;
		--out)
			OUT_TEMPLATE="$2"; shift 2;;
		--out=*)
			OUT_TEMPLATE="${1#--out=}"; shift;;
		--help|-h)
			usage; exit 0;;
		--)
			shift; break;;
		-*)
			EXTRA_ARGS+=("$1"); shift
			if [[ $# -gt 0 && ! "$1" == -* ]]; then
				EXTRA_ARGS+=("$1"); shift
			fi
			;;
		*)
			if [ ${#TIMES[@]} -eq 0 ] && [ -z "$TIMES_FILE" ] && [ -z "$TIMES_FILE_LINES" ]; then
				IFS=',' read -ra parts <<< "$1"
				for p in "${parts[@]}"; do
					for q in $p; do TIMES+=("$q"); done
				done
				shift
			else
				EXTRA_ARGS+=("$1"); shift
			fi
			;;
	esac
done

# If --Ks was present on command line, add it to EXTRA_ARGS so it is forwarded
if [[ ${#KS[@]} -gt 0 ]]; then
    EXTRA_ARGS+=(--Ks)
    for k in "${KS[@]}"; do EXTRA_ARGS+=("$k"); done
fi

if [[ -n "$KS_FILE" ]]; then
	if [[ ! -f "$KS_FILE" ]]; then echo "file not found: $KS_FILE" >&2; exit 2; fi
	mapfile -t vals < <(grep -v '^#' "$KS_FILE" | tr '\n' ' ')
	KS=( ${vals[@]} )
fi

if [[ -n "$THETA_FILE" ]]; then
	if [[ ! -f "$THETA_FILE" ]]; then echo "file not found: $THETA_FILE" >&2; exit 2; fi
	mapfile -t vals < <(grep -v '^#' "$THETA_FILE" | tr '\n' ' ')
	# prepend --theta to EXTRA_ARGS
	EXTRA_ARGS+=(--theta)
	for v in ${vals[@]}; do EXTRA_ARGS+=("$v"); done
	# also pass matching --K so the Python script does not reject the provided theta
	EXTRA_ARGS+=(--K "${#vals[@]}")
fi

# expand eps file
if [[ -n "${EPS_FILE}" ]]; then
	if [[ -f "$EPS_FILE" ]]; then
		mapfile -t _eps_lines < <(grep -v '^#' "$EPS_FILE" | tr '\n' ' ')
		EXTRA_ARGS+=(--epsilons)
		for v in ${_eps_lines[@]}; do EXTRA_ARGS+=("$v"); done
	else
		echo "epsilons file not found: $EPS_FILE" >&2; exit 2
	fi
fi

if [[ -n "$TIMES_FILE_LINES" ]]; then
	if [[ ! -f "$TIMES_FILE_LINES" ]]; then echo "file not found: $TIMES_FILE_LINES" >&2; exit 2; fi
	n=1
	while IFS= read -r line || [[ -n "$line" ]]; do
		line="$(printf '%s' "$line" | sed -e 's/^\s*//' -e 's/\s*$//')"
		[[ -z "$line" || "${line:0:1}" == "#" ]] && continue
		read -ra tokens <<< "$(printf '%s' "$line" | tr ',' ' ')"
		# separate leading numeric time tokens from option tokens
		times_tokens=()
		line_opts=()
		i=0
		while [[ $i -lt ${#tokens[@]} ]]; do
			tok=${tokens[$i]}
			if [[ "$tok" == -* ]]; then
				# option flag; include possible value if next token doesn't start with '-'
				line_opts+=("$tok")
				if [[ $((i+1)) -lt ${#tokens[@]} ]]; then
					next=${tokens[$((i+1))]}
					if [[ "$next" != -* ]]; then
						line_opts+=("$next")
						i=$((i+1))
					fi
				fi
			else
				times_tokens+=("$tok")
			fi
			i=$((i+1))
		done

		# prepare per-run EXTRA_ARGS with unique out and per-line options
		OLD_EXTRA=("${EXTRA_ARGS[@]:-}")
		if [[ -n "$OUT_TEMPLATE" ]]; then
			EXTRA_ARGS+=(--out "$(make_out_name "$OUT_TEMPLATE" $n)")
		else
			EXTRA_ARGS+=(--out "./output_${n}.png")
		fi
		# append line-specific options
		for o in "${line_opts[@]:-}"; do EXTRA_ARGS+=("$o"); done

		run_once "${times_tokens[@]}"
		EXTRA_ARGS=("${OLD_EXTRA[@]:-}")
		n=$((n+1))
	done < "$TIMES_FILE_LINES"
	exit 0
fi

if [[ -n "$EPS_FILE_LINES" ]]; then
	if [[ ! -f "$EPS_FILE_LINES" ]]; then echo "file not found: $EPS_FILE_LINES" >&2; exit 2; fi
	n=1
	while IFS= read -r line || [[ -n "$line" ]]; do
		line="$(printf '%s' "$line" | sed -e 's/^\s*//' -e 's/\s*$//')"
		[[ -z "$line" || "${line:0:1}" == "#" ]] && continue
		read -ra tokens <<< "$(printf '%s' "$line" | tr ',' ' ')"
		# separate leading epsilon tokens from option tokens
		eps_tokens=()
		line_opts=()
		i=0
		while [[ $i -lt ${#tokens[@]} ]]; do
			tok=${tokens[$i]}
			if [[ "$tok" == -* ]]; then
				line_opts+=("$tok")
				if [[ $((i+1)) -lt ${#tokens[@]} ]]; then
					next=${tokens[$((i+1))]}
					if [[ "$next" != -* ]]; then
						line_opts+=("$next")
						i=$((i+1))
					fi
				fi
			else
				eps_tokens+=("$tok")
			fi
			i=$((i+1))
		done

		OLD_EXTRA=("${EXTRA_ARGS[@]:-}")
		if [[ -n "$OUT_TEMPLATE" ]]; then
			EXTRA_ARGS+=(--out "$(make_out_name "$OUT_TEMPLATE" $n)")
		else
			EXTRA_ARGS+=(--out "./output_eps_${n}.png")
		fi
		for o in "${line_opts[@]:-}"; do EXTRA_ARGS+=("$o"); done
		run_eps_once "${eps_tokens[@]}"
		EXTRA_ARGS=("${OLD_EXTRA[@]:-}")
		n=$((n+1))
	done < "$EPS_FILE_LINES"
	exit 0
fi

if [[ -n "$KS_FILE_LINES" ]]; then
	if [[ ! -f "$KS_FILE_LINES" ]]; then echo "file not found: $KS_FILE_LINES" >&2; exit 2; fi
	n=1
	while IFS= read -r line || [[ -n "$line" ]]; do
		line="$(printf '%s' "$line" | sed -e 's/^\s*//' -e 's/\s*$//')"
		[[ -z "$line" || "${line:0:1}" == "#" ]] && continue
		read -ra tokens <<< "$(printf '%s' "$line" | tr ',' ' ')"
		# separate leading K tokens from option tokens
		ks_tokens=()
		line_opts=()
		i=0
		while [[ $i -lt ${#tokens[@]} ]]; do
			tok=${tokens[$i]}
			if [[ "$tok" == -* ]]; then
				line_opts+=("$tok")
				if [[ $((i+1)) -lt ${#tokens[@]} ]]; then
					next=${tokens[$((i+1))]}
					if [[ "$next" != -* ]]; then
						line_opts+=("$next")
						i=$((i+1))
					fi
				fi
			else
				ks_tokens+=("$tok")
			fi
			i=$((i+1))
		done

		OLD_EXTRA=("${EXTRA_ARGS[@]:-}")
		if [[ -n "$OUT_TEMPLATE" ]]; then
			EXTRA_ARGS+=(--out "$(make_out_name "$OUT_TEMPLATE" $n)")
		else
			EXTRA_ARGS+=(--out "./output_K_${n}.png")
		fi
		for o in "${line_opts[@]:-}"; do EXTRA_ARGS+=("$o"); done
		run_K_once "${ks_tokens[@]}"
		EXTRA_ARGS=("${OLD_EXTRA[@]:-}")
		n=$((n+1))
	done < "$KS_FILE_LINES"
	exit 0
fi

if [[ -n "$THETA_FILE_LINES" ]]; then
	if [[ ! -f "$THETA_FILE_LINES" ]]; then echo "file not found: $THETA_FILE_LINES" >&2; exit 2; fi
	n=1
	total=$(grep -v '^#' "$THETA_FILE_LINES" | sed -e '/^\s*$/d' | wc -l)
	while IFS= read -r line || [[ -n "$line" ]]; do
		line="$(printf '%s' "$line" | sed -e 's/^\s*//' -e 's/\s*$//')"
		[[ -z "$line" || "${line:0:1}" == "#" ]] && continue
		read -ra tokens <<< "$(printf '%s' "$line" | tr ',' ' ')"
		# separate leading theta tokens from option tokens
		theta_tokens=()
		line_opts=()
		i=0
		while [[ $i -lt ${#tokens[@]} ]]; do
			tok=${tokens[$i]}
			if [[ "$tok" == -* ]]; then
				line_opts+=("$tok")
				if [[ $((i+1)) -lt ${#tokens[@]} ]]; then
					next=${tokens[$((i+1))]}
					if [[ "$next" != -* ]]; then
						line_opts+=("$next")
						i=$((i+1))
					fi
				fi
			else
				theta_tokens+=("$tok")
			fi
			i=$((i+1))
		done

		OLD_EXTRA=("${EXTRA_ARGS[@]:-}")
		if [[ -n "$OUT_TEMPLATE" ]]; then
			EXTRA_ARGS+=(--out "$(make_out_name "$OUT_TEMPLATE" $n)")
		else
			EXTRA_ARGS+=(--out "./output_theta_${n}.png")
		fi
		for o in "${line_opts[@]:-}"; do EXTRA_ARGS+=("$o"); done
		# add per-run theta values as args to the generic runner
		local_k=${#theta_tokens[@]}
		echo "Job $n/$total — running theta: ${theta_tokens[*]} (K=${local_k})"
		run_generic --theta "${theta_tokens[@]}" --K "$local_k"
		EXTRA_ARGS=("${OLD_EXTRA[@]:-}")
		n=$((n+1))
	done < "$THETA_FILE_LINES"
	exit 0
fi



if [[ -n "$TIMES_FILE" ]]; then
	if [[ ! -f "$TIMES_FILE" ]]; then echo "file not found: $TIMES_FILE" >&2; exit 2; fi
	mapfile -t vals < <(grep -v '^#' "$TIMES_FILE" | tr '\n' ' ')
	TIMES=( ${vals[@]} )
fi

if [[ ${#TIMES[@]} -gt 0 ]]; then
	run_once "${TIMES[@]}"
	exit 0
fi

if [[ ${#KS[@]} -gt 0 ]]; then
	run_K_once "${KS[@]}"
	exit 0
fi

usage
exit 1


