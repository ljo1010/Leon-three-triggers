/* ===== LEON: Three Triggers - Story JavaScript ===== */

/* 디버그 메뉴 링크 표시 여부 (제출 직전 false로!) */
setup.showDebug = false;

/* ★ 디버그용 고속 모드: <<timed>>/<<next>> 서스펜스 딜레이를 제거해 즉시 표시.
   제출 직전 반드시 false 로! (false면 원래 정전 페이싱 그대로) */
setup.fastMode = false;

(function () {
    if (!setup.fastMode) return;
    try {
        var t = Macro.get('timed');
        if (!t || t.__fastPatched) return;
        var orig = t.handler;
        var TIME = /^\s*[\d.]+\s*(ms|s)\s*$/;
        function zeroDelays(args) {
            if (!args) return;
            for (var i = 0; i < args.length; i++) {
                if (typeof args[i] === 'string' && TIME.test(args[i])) args[i] = '0ms';
            }
        }
        t.handler = function () {
            zeroDelays(this.args);
            if (this.payload) {
                for (var k = 0; k < this.payload.length; k++) zeroDelays(this.payload[k].args);
            }
            return orig.apply(this, arguments);
        };
        t.__fastPatched = true;
    } catch (e) { console.log('fastMode patch skipped: ' + e); }
})();

/* 이미지 클릭 시 확대 (라이트박스) */
$(document).on('click', '.scene-image, .clue-image, .character-portrait, .prop, .qr-image', function () {
    var src = $(this).attr('src');
    if (!src) return;
    var $ov = $('<div class="lightbox-overlay"><img class="lightbox-img" src="' + src + '" alt=""></div>');
    $('body').append($ov);
    requestAnimationFrame(function () { $ov.addClass('show'); });
});
function closeLightbox() {
    var $ov = $('.lightbox-overlay');
    if (!$ov.length) return;
    $ov.removeClass('show');
    setTimeout(function () { $ov.remove(); }, 250);
}
$(document).on('click', '.lightbox-overlay', closeLightbox);
$(document).on('keydown', function (e) { if (e.key === 'Escape') closeLightbox(); });

/* 페이지 이동 시 본문을 맨 위로. #story가 fixed+overflow 스크롤 컨테이너라
   SugarCube 기본 윈도우 스크롤이 먹지 않으므로 직접 올려준다. */
$(document).on(':passagedisplay', function () {
    const el = document.getElementById('story');
    if (el) el.scrollTop = 0;
});

/* 시점 자동 판별: 패시지 태그([leon]/[mathilda]/[stansfield])로 $perspective 설정.
   각 패시지에서 일일이 <<set $perspective>> 안 해도 항상 맞게. */
$(document).on(':passagestart', function (ev) {
    const tags = (ev.passage && ev.passage.tags) || [];
    if (tags.includes('leon'))            State.variables.perspective = 'leon';
    else if (tags.includes('mathilda'))   State.variables.perspective = 'mathilda';
    else if (tags.includes('stansfield')) State.variables.perspective = 'stansfield';
});

/* 시점 전환 시 body 클래스 자동 갱신 */
$(document).on(':passagerender', function () {
    const pov = State.variables.perspective;
    document.body.classList.remove('pov-mathilda', 'pov-leon', 'pov-stansfield');
    if (pov && pov !== 'intro') {
        document.body.classList.add('pov-' + pov);
    }
});

/* 화면 흔들림: <<shake>> */
Macro.add('shake', {
    handler: function () {
        $('body').addClass('shake');
        setTimeout(() => $('body').removeClass('shake'), 600);
    }
});

/* 플래시 (번쩍): <<flash>> */
Macro.add('flash', {
    handler: function () {
        $('body').addClass('flash');
        setTimeout(() => $('body').removeClass('flash'), 200);
    }
});

/* 단서 추가 + 토스트: <<clue "단서명">> */
Macro.add('clue', {
    handler: function () {
        const clueName = this.args[0];
        if (!State.variables.clues) State.variables.clues = [];
        if (State.variables.clues.includes(clueName)) return;   /* 중복 단서 방지 (재방문/뒤로가기) */
        State.variables.clues.push(clueName);
        const $toast = $('<div class="clue-toast">+ 단서: ' + clueName + '</div>');
        $(this.output).append($toast);
    }
});

/* ===== 스탯 라벨 (게이트 태그/HUD 공용) ===== */
setup.statLabels = {
    'leon.attachment':    '애착',
    'leon.discipline':    '규율',
    'leon.suspicion':     '경계심',
    'mathilda.trust':     '신뢰',
    'mathilda.rage':      '분노',
    'mathilda.skill':     '기술',
    'stansfield.high':    '약물',
    'stansfield.cruelty': '잔혹도'
};

/* 경로 문자열("leon.discipline")로 중첩 변수 값 읽기 */
function statValue(path) {
    const [obj, key] = String(path).split('.');
    const root = State.variables[obj];
    return (root && typeof root[key] === 'number') ? root[key] : 0;
}

/* ===== 임계값 선택지 (베데스다식): =====
   <<gate "leon.discipline" 5 "Leon_07_Refuse">>차갑게 거절한다<</gate>>
   스탯이 임계값 이상이면 특별 선택지 해금, 미만이면 잠긴 채 요구치 표시. */
Macro.add('gate', {
    tags: null,
    handler: function () {
        const path      = this.args[0];
        const threshold = this.args[1];
        const passage   = this.args[2];
        const fx        = this.args[3] || '';   /* 효과 미리보기 텍스트 */
        const label     = this.payload[0].contents.trim();
        const statLabel = setup.statLabels[path] || path;
        const met       = statValue(path) >= threshold;
        const fxHtml    = fx ? '<span class="fx-tag">' + fx + '</span>' : '';

        if (met) {
            const $wrap = $('<div class="gate-choice gate-unlocked"></div>');
            $(this.output).append($wrap);
            new Wikifier($wrap[0], '[[' + label + '|' + passage + ']]');
            $wrap.find('a').prepend(
                '<span class="gate-tag">❖ ' + statLabel + ' ' + threshold + '</span> '
            );
            if (fx) $wrap.find('a').append(fxHtml);
        } else {
            const $locked = $(
                '<div class="gate-choice gate-locked">' +
                '<span class="gate-tag gate-tag-locked">🔒 ' + statLabel + ' ' + threshold + ' 필요</span> ' +
                label + fxHtml + '</div>'
            );
            $(this.output).append($locked);
        }
    }
});

/* 효과 미리보기 선택지: <<pick "패시지" "라벨" "효과텍스트" "셋터(선택)">>
   효과 태그를 링크 우측에 표시. 셋터를 주면 클릭 시 실행(셋터 링크 대체).
   (이름이 'choice'면 SugarCube 내장 <<choice>>와 충돌하므로 'pick' 사용) */
Macro.add('pick', {
    handler: function () {
        const passage = this.args[0];
        const label   = this.args[1];
        const fx      = this.args[2] || '';
        const setter  = this.args[3] || '';
        const $wrap = $('<div class="choice-row"></div>');
        $(this.output).append($wrap);
        const markup = '<<link ' + JSON.stringify(label) + '>>'
                     + (setter ? '<<set ' + setter + '>>' : '')
                     + '<<goto ' + JSON.stringify(passage) + '>><</link>>';
        new Wikifier($wrap[0], markup);
        const $a = $wrap.find('a').addClass('link-internal');
        if (fx) $a.append('<span class="fx-tag">' + fx + '</span>');
    }
});

/* 소지품 추가 + 토스트: <<item "베레타 92FS">>  (체크는 $inventory.includes(...)) */
Macro.add('item', {
    handler: function () {
        const name = this.args[0];
        if (!State.variables.inventory) State.variables.inventory = [];
        if (!State.variables.inventory.includes(name)) {
            State.variables.inventory.push(name);
            $(this.output).append(
                $('<div class="clue-toast item-toast">+ 소지품: ' + name + '</div>')
            );
        }
    }
});

/* 엔딩 플래그 설정 (중앙 집중): <<flag "killedTony">> 또는 <<flag "route" "revenge">> */
Macro.add('flag', {
    handler: function () {
        const name = this.args[0];
        const val  = this.args.length > 1 ? this.args[1] : true;
        if (!State.variables.endingFlags) State.variables.endingFlags = {};
        State.variables.endingFlags[name] = val;
    }
});

/* ===== HUD 자동 업데이트 ===== */
$(document).on(':passagedisplay', function () {
    /* 기존 HUD 제거 */
    $('#hud').remove();

    const sv = State.variables;
    const pov = sv.perspective || 'intro';

    /* 시점별 라벨 + 스탯 구성 */
    let povLabel = '';
    let statsHtml = '';

    /* 스탯 한 칸 만들기 (active=현재 시점이면 밝게) */
    function stat(label, value, active) {
        return '<span class="hud-stat' + (active ? ' hud-stat-active' : '') + '">'
             + label + '<span class="hud-stat-value">' + value + '</span></span>';
    }

    if (pov === 'stansfield') {
        povLabel = 'STANSFIELD';
        statsHtml = stat('약물', sv.stansfield.high, true)
                  + stat('잔혹도', sv.stansfield.cruelty, true);
    } else if (pov === 'leon' || pov === 'mathilda') {
        povLabel = (pov === 'leon') ? 'LÉON' : 'MATHILDA';
        const leonActive = (pov === 'leon');
        /* 레옹·마틸다는 한 쌍 — 두 인물 스탯을 모두 표시. 게이트가 서로를 참조하므로. */
        const leonGroup = stat('애착', sv.leon.attachment, leonActive)
                        + stat('규율', sv.leon.discipline, leonActive)
                        + stat('경계심', sv.leon.suspicion, leonActive);
        const mathildaGroup = stat('신뢰', sv.mathilda.trust, !leonActive)
                            + stat('분노', sv.mathilda.rage, !leonActive)
                            + stat('기술', sv.mathilda.skill, !leonActive);
        statsHtml = '<span class="hud-group">' + leonGroup + '</span>'
                  + '<span class="hud-sep">·</span>'
                  + '<span class="hud-group">' + mathildaGroup + '</span>';
    } else {
        return;  /* intro면 HUD 안 띄움 */
    }

    /* 단서 개수 */
    const clueCount = (sv.clues && sv.clues.length) || 0;
    const cluesHtml = clueCount > 0
        ? `<span class="hud-clues">단서<span class="hud-clues-count">${clueCount}</span></span>`
        : `<span class="hud-clues" style="opacity:0.3;">단서<span class="hud-clues-count">0</span></span>`;

    /* HUD 삽입 */
    const hudHtml = `
        <div id="hud">
            <span class="hud-pov">▸ ${povLabel}</span>
            <span class="hud-stats">${statsHtml}</span>
            ${cluesHtml}
        </div>
    `;
    $('body').append(hudHtml);
});

/* 단서 클릭하면 단서 목록 모달 표시 (라이트박스와 동일한 연출) */
function closeClueModal() {
    const $ov = $('.clue-modal-overlay');
    if (!$ov.length) return;
    $ov.removeClass('show');
    setTimeout(() => $ov.remove(), 250);
}
$(document).on('click', '.hud-clues', function () {
    const clues = State.variables.clues || [];
    if (clues.length === 0 || $('.clue-modal-overlay').length) return;
    const items = clues.map((c, i) =>
        '<li class="clue-row" style="animation-delay:' + (i * 45) + 'ms">' +
            '<span class="clue-num">' + String(i + 1).padStart(2, '0') + '</span>' +
            '<span class="clue-text">' + c + '</span>' +
        '</li>'
    ).join('');
    const $ov = $(
        '<div class="clue-modal-overlay">' +
            '<div class="clue-modal" role="dialog" aria-modal="true" aria-label="발견한 단서">' +
                '<div class="clue-modal-head">' +
                    '<span class="clue-modal-title">발견한 단서</span>' +
                    '<span class="clue-modal-count">' + clues.length + '</span>' +
                '</div>' +
                '<ul class="clue-list">' + items + '</ul>' +
                '<button type="button" class="clue-modal-close">닫기  ✕</button>' +
            '</div>' +
        '</div>'
    );
    $('body').append($ov);
    requestAnimationFrame(() => $ov.addClass('show'));
});
/* 바깥/닫기 버튼 클릭으로 닫기 (모달 내부 클릭은 유지) */
$(document).on('click', '.clue-modal-overlay', function (e) {
    if (e.target === this || $(e.target).hasClass('clue-modal-close')) closeClueModal();
});
$(document).on('keydown', function (e) { if (e.key === 'Escape') closeClueModal(); });

/* HUD 단서 부분만 클릭 가능하게 */
$(document).on(':passagedisplay', function () {
    setTimeout(() => {
        $('.hud-clues').css('pointer-events', 'auto').css('cursor', 'pointer');
    }, 100);
});

/* ===== 사운드 시스템 초기화 ===== */
/* 파일은 audio/ 폴더에 mp3로 저장 (예: audio/leon_theme.mp3) */

/* BGM (배경음악) */
SimpleAudio.tracks.add('bgm_leon',       'audio/bgm_leon.mp3');
SimpleAudio.tracks.add('bgm_mathilda',   'audio/bgm_mathilda.mp3');
SimpleAudio.tracks.add('bgm_stansfield', 'audio/bgm_stansfield.mp3');
SimpleAudio.tracks.add('bgm_tense',      'audio/bgm_tense.mp3');
SimpleAudio.tracks.add('bgm_ending',     'audio/bgm_ending.mp3');  /* 엔딩 곡 (원작: Sting - Shape of My Heart / 저작권 음원은 직접 배치) */

/* SFX (효과음) — 실제 사용되는 것만 등록 (미사용 트랙은 로드 시 404 방지 위해 제외) */
SimpleAudio.tracks.add('sfx_gunshot',    'audio/sfx_gunshot.mp3');    /* 단발 + 잔향 */
SimpleAudio.tracks.add('sfx_gunshot2',   'audio/sfx_gunshot2.mp3');   /* 짧고 날카로운 크랙 */
SimpleAudio.tracks.add('sfx_gunshot3',   'audio/sfx_gunshot3.mp3');   /* 묵직한 저음 */
SimpleAudio.tracks.add('sfx_heartbeat',  'audio/sfx_heartbeat.mp3');
SimpleAudio.tracks.add('sfx_door_knock', 'audio/sfx_door_knock.mp3'); /* 문 두드림 (똑.똑.똑.) */
SimpleAudio.tracks.add('sfx_shotgun',    'audio/sfx_shotgun.mp3');    /* 샷건 4발 (벽 너머 처형) */

/* 시점별 BGM 자동 전환 그룹 */
SimpleAudio.lists.add('bgm_all', 'bgm_leon', 'bgm_mathilda', 'bgm_stansfield', 'bgm_tense', 'bgm_ending');

/* 총성: <<gunshot>> — 매번 사운드/흔들림/플래시를 무작위로 변주해 단조로움 제거.
   선택 인자: <<gunshot "soft">> / <<gunshot "hard">> 로 강도 고정 가능. */
var GUNSHOT_SFX = ['sfx_gunshot', 'sfx_gunshot2', 'sfx_gunshot3'];
Macro.add('gunshot', {
    handler: function () {
        const force = this.args[0];                       /* "soft" | "hard" | "shotgun" | undefined */
        const rnd = (a, b) => a + Math.random() * (b - a);

        /* 1) 사운드: "shotgun"이면 샷건 고정, 아니면 세 변형 중 무작위 + 볼륨 미세 변주 */
        try {
            const pick = (force === 'shotgun')
                ? 'sfx_shotgun'
                : GUNSHOT_SFX[Math.floor(Math.random() * GUNSHOT_SFX.length)];
            const tr = SimpleAudio.tracks.get(pick);
            if (tr) { tr.volume(force === 'shotgun' ? 1.0 : rnd(0.72, 1.0)); tr.stop(); tr.play(); }
        } catch (e) { /* 파일 없어도 게임 계속 */ }

        /* 2) 흔들림: 강도 무작위(soft/기본/hard) */
        let shakeCls = 'shake';
        if (force === 'soft') shakeCls = 'shake--soft';
        else if (force === 'hard') shakeCls = 'shake--hard';
        else shakeCls = ['shake--soft', 'shake', 'shake', 'shake--hard'][Math.floor(Math.random() * 4)];

        /* 3) 플래시: 밝기·지속 무작위 (CSS 변수로 전달) */
        const flashA = force === 'soft' ? rnd(0.30, 0.45)
                     : force === 'hard' ? rnd(0.70, 0.92)
                     : rnd(0.42, 0.80);
        const root = document.documentElement;
        root.style.setProperty('--flash-a', flashA.toFixed(2));
        root.style.setProperty('--flash-d', rnd(0.12, 0.22).toFixed(3) + 's');

        const $b = $('body').removeClass('shake shake--soft shake--hard flash');
        void document.body.offsetWidth;                   /* reflow → 애니메이션 재시작 보장 */
        $b.addClass(shakeCls).addClass('flash');
        setTimeout(() => { $b.removeClass(shakeCls + ' flash'); }, 700);
    }
});

/* SFX 재생 매크로: <<sfx "이름">> */
Macro.add('sfx', {
    handler: function () {
        const name = this.args[0];
        try {
            const track = SimpleAudio.tracks.get('sfx_' + name);
            if (track) track.play();
        } catch (e) {
            console.log('SFX not found: ' + name);
        }
    }
});

/* BGM 재생 매크로: <<bgm "이름">> / <<bgm "stop">>
   ★ 핵심 수정: SugarCube의 list.stop()은 '페이드 진행 중'인 트랙을 멈추지 못해
      새 BGM과 옛 BGM이 겹쳤다. → 트랙마다 fadeStop()으로 페이드 타이머를 먼저
      취소한 뒤 stop() 해야 확실히 멈춘다. 같은 곡이 이미 재생 중이면 재시작하지 않는다. */
var BGM_IDS = ['bgm_leon', 'bgm_mathilda', 'bgm_stansfield', 'bgm_tense', 'bgm_ending'];
Macro.add('bgm', {
    handler: function () {
        const name = this.args[0];
        const target = (name === 'stop' || !name) ? null : 'bgm_' + name;
        try {
            /* 이미 같은 곡이 흐르고 있으면 그대로 둔다 (장면마다 재시작되는 끊김 방지) */
            if (target && setup._bgmCur === target) {
                const cur = SimpleAudio.tracks.get(target);
                if (cur && cur.isPlaying()) return;
            }

            /* 모든 BGM을 확실히 정지: 페이드 취소 → 정지 */
            BGM_IDS.forEach(function (id) {
                const tr = SimpleAudio.tracks.get(id);
                if (!tr) return;
                try { tr.fadeStop(); } catch (e) {}
                try { tr.stop(); } catch (e) {}
            });

            setup._bgmCur = target;
            if (!target) return;

            const track = SimpleAudio.tracks.get(target);
            if (track) {
                track.loop(true);
                track.volume(0);
                track.fade(2, 0.5, 0);   /* 2초간 0 → 0.5 페이드인 */
            }
        } catch (e) {
            console.log('BGM error: ' + name);
        }
    }
});

/* 사운드 마스터 토글 (ON/OFF) */
window.toggleSound = function() {
    const muted = SimpleAudio.mute();
    SimpleAudio.mute(!muted);
    $('#sound-toggle').text(muted ? '🔊' : '🔇');
};

$(document).on(':storyready', function() {
    if ($('#sound-toggle').length === 0) {
        $('body').append('<button id="sound-toggle" onclick="toggleSound()">🔊</button>');
    }
});

/* 숨은 디버그 단축키: Ctrl + Shift + D → 디버그 메뉴(Debug_Jump)로 점프.
   화면에 링크는 숨긴 채(showDebug=false)도 동작 → 제출본에서 발표용 빠른 점프에 사용.
   Ctrl + Shift + S → 사운드 음소거 토글. */
$(document).on('keydown', function (ev) {
    if (!ev.ctrlKey || !ev.shiftKey) return;
    const k = (ev.key || '').toLowerCase();
    if (k === 'd' || ev.keyCode === 68) {
        ev.preventDefault();
        try {
            if (window.SugarCube && SugarCube.State.passage !== 'Debug_Jump') {
                SugarCube.Engine.play('Debug_Jump');
            }
        } catch (e) { /* Debug_Jump 없으면 무시 */ }
    } else if (k === 's' || ev.keyCode === 83) {
        ev.preventDefault();
        if (window.toggleSound) window.toggleSound();
    }
});
