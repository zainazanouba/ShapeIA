import { useEffect, useRef, useState } from 'react';
import Plot from 'react-plotly.js';
import { BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

const SHAPE_EXAMPLES = [
  'Dessine un cube rouge de 5',
  'Kora bleue 10',
  'Un cercle 4 et un carre 6',
  'Dessine une pyramide avec une base de 6 et une hauteur de 8',
  'Dessine un cube rouge et une sphere bleue'
];

const FUNCTION_EXAMPLES = [
  'f(x)=sin(x) domain [-5,5]',
  'f(x,y)=cos(x)*sin(y) domain [-5,5]',
  'f(x)=x^2 + 2x + 1 domain [-3,3]'
];

function buildPlotProps(shape) {
  if (!shape || !shape.axes) return null;
  const { axes, render, type, color } = shape;
  const { x, y, z } = axes || {};
  const is2d = render === 'line2d';
  if (is2d) {
    if (!x || !y) return null;
  } else if (!x || !y || !z) {
    return null;
  }

  const flatten = (value, out) => {
    if (Array.isArray(value)) {
      value.forEach((item) => flatten(item, out));
      return;
    }
    if (typeof value === 'number' && Number.isFinite(value)) {
      out.push(value);
    }
  };

  const getRange = (value) => {
    const values = [];
    flatten(value, values);
    if (values.length === 0) return null;
    let min = values[0];
    let max = values[0];
    for (let i = 1; i < values.length; i += 1) {
      const v = values[i];
      if (v < min) min = v;
      if (v > max) max = v;
    }
    if (min === max) {
      const pad = Math.max(1, Math.abs(min) * 0.25);
      return [min - pad, max + pad];
    }
    const pad = (max - min) * 0.1;
    return [min - pad, max + pad];
  };

  const xRange = getRange(x);
  const yRange = getRange(y);
  const zRange = is2d ? null : getRange(z);

  const data = [];
  const lineColor = color || '#c1e328';

  if (is2d) {
    data.push({
      type: 'scatter',
      x,
      y,
      mode: 'lines',
      line: { color: lineColor, width: 3 }
    });
  } else if (render === 'surface') {
    data.push({
      type: 'surface',
      x,
      y,
      z,
      colorscale: [
        [0, '#98b999'],
        [1, lineColor]
      ],
      showscale: false,
      opacity: 0.9
    });
  } else if (render === 'wireframe') {
    data.push({
      type: 'scatter3d',
      x,
      y,
      z,
      mode: 'lines+markers',
      line: { color: lineColor, width: 6 },
      marker: { size: 4, color: '#d62728' }
    });
  } else {
    data.push({
      type: 'scatter3d',
      x,
      y,
      z,
      mode: 'lines',
      line: { color: lineColor, width: 8 }
    });
  }

  const layout = is2d
    ? {
        autosize: true,
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: {
          title: { text: 'X', font: { color: 'red' } },
          range: xRange || undefined,
          autorange: !xRange,
          showticklabels: true,
          ticks: 'outside',
          tickfont: { color: '#475569' },
          tickcolor: 'rgba(15, 23, 42, 0.4)',
          showgrid: true,
          gridcolor: 'rgba(15, 23, 42, 0.08)',
          gridwidth: 1,
          zeroline: true,
          zerolinecolor: 'rgba(15, 23, 42, 0.5)',
          zerolinewidth: 1.2,
          showline: true,
          linecolor: 'rgba(15, 23, 42, 0.4)',
          linewidth: 1
        },
        yaxis: {
          title: { text: 'Y', font: { color: 'green' } },
          range: yRange || undefined,
          autorange: !yRange,
          showticklabels: true,
          ticks: 'outside',
          tickfont: { color: '#475569' },
          tickcolor: 'rgba(15, 23, 42, 0.4)',
          showgrid: true,
          gridcolor: 'rgba(15, 23, 42, 0.08)',
          gridwidth: 1,
          zeroline: true,
          zerolinecolor: 'rgba(15, 23, 42, 0.5)',
          zerolinewidth: 1.2,
          showline: true,
          linecolor: 'rgba(15, 23, 42, 0.4)',
          linewidth: 1
        }
      }
    : {
        autosize: true,
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        scene: {
          aspectmode: 'cube',
          camera:
            type === '3D'
              ? {
                  eye: { x: 1.5, y: 1.5, z: 1.5 },
                  projection: { type: 'perspective' }
                }
              : { eye: { x: 0, y: 0, z: 2.5 } },
          xaxis: {
            title: { text: 'X', font: { color: 'red' } },
            range: xRange || undefined,
            autorange: !xRange
          },
          yaxis: {
            title: { text: 'Y', font: { color: 'green' } },
            range: yRange || undefined,
            autorange: !yRange
          },
          zaxis: {
            title: { text: 'Z', font: { color: 'blue' } },
            range: zRange || undefined,
            autorange: !zRange
          }
        }
      };

  return {
    data,
    layout,
    config: { displayModeBar: false, responsive: true }
  };
}

export default function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('shapes');
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeMessageId, setActiveMessageId] = useState(null);
  const [chatOpen, setChatOpen] = useState(() => {
    if (typeof window === 'undefined') return true;
    try {
      const saved = window.localStorage.getItem('shapeia_chat_open');
      return saved === null ? true : saved === 'true';
    } catch (error) {
      return true;
    }
  });

  const endRef = useRef(null);
  const formRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const fireResize = () => window.dispatchEvent(new Event('resize'));
    const t1 = window.setTimeout(fireResize, 60);
    const t2 = window.setTimeout(fireResize, 420);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
    };
  }, [chatOpen]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        window.localStorage.setItem('shapeia_chat_open', String(chatOpen));
      } catch (error) {
      }
    }
  }, [chatOpen]);

  const lastShapeMessage = [...messages].reverse().find((msg) => msg.shapes?.length);
  const activeMessage =
    messages.find((msg) => msg.id === activeMessageId) || lastShapeMessage || null;
  const activeShapes = activeMessage?.shapes || [];
  const activeShape = activeShapes[activeIndex] ?? null;
  const plotProps = buildPlotProps(activeShape);

  const examples = mode === 'functions' ? FUNCTION_EXAMPLES : SHAPE_EXAMPLES;
  const placeholder =
    mode === 'functions'
      ? 'Ex: f(x)=sin(x) domain [-5,5]'
      : 'Ex: Dessine un cube rouge de 5';

  const canSend = input.trim().length > 0 && !loading;

  const handleSubmit = async (event) => {
    event.preventDefault();
    const text = input.trim();
    if (!text) return;

    const stamp = Date.now();
    const userMessage = {
      id: `${stamp}-user`,
      role: 'user',
      text
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, mode })
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload?.detail || 'Request failed');
      }

      const newShapes = payload.shapes || [];
      const assistantMessage = {
        id: `${stamp}-assistant`,
        role: 'assistant',
        text: payload.message || 'Ok',
        shapeCount: newShapes.length,
        shapes: newShapes
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (newShapes.length > 0) {
        setActiveMessageId(assistantMessage.id);
        setActiveIndex(0);
      }
    } catch (error) {
      const assistantMessage = {
        id: `${stamp}-error`,
        role: 'assistant',
        text: error?.message || 'Request failed',
        status: 'error'
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setActiveIndex(0);
    setActiveMessageId(null);
  };

  return (
    <div className={`app ${chatOpen ? 'chat-open' : 'chat-closed'}`}>
      <button
        className='chat-backdrop'
        type='button'
        aria-label='Close chat'
        onClick={() => setChatOpen(false)}
      />
      {!chatOpen && (
        <button
          className='chat-toggle-fab'
          type='button'
          title='Open chat'
          aria-label='Open chat'
          onClick={() => setChatOpen(true)}
        >
          <svg className='toggle-icon chat' viewBox='0 0 24 24' aria-hidden='true'>
            <path
              d='M20 12a7 7 0 0 1-7 7H8l-4 3V12a7 7 0 0 1 7-7h2a7 7 0 0 1 7 7Z'
              fill='none'
              stroke='currentColor'
              strokeWidth='2'
              strokeLinejoin='round'
            />
          </svg>
          <svg className='toggle-icon chevron' viewBox='0 0 24 24' aria-hidden='true'>
            <path
              d='M15 18l-6-6 6-6'
              fill='none'
              stroke='currentColor'
              strokeWidth='2'
              strokeLinecap='round'
              strokeLinejoin='round'
            />
          </svg>
        </button>
      )}

      <section className={`chat-panel ${chatOpen ? 'open' : 'closed'}`}>
        <div className='panel chat-drawer'>
          <button
            className='chat-toggle'
            type='button'
            title={chatOpen ? 'Close chat' : 'Open chat'}
            aria-label={chatOpen ? 'Close chat' : 'Open chat'}
            onClick={() => setChatOpen((prev) => !prev)}
          >
            <svg className='toggle-icon chat' viewBox='0 0 24 24' aria-hidden='true'>
              <path
                d='M20 12a7 7 0 0 1-7 7H8l-4 3V12a7 7 0 0 1 7-7h2a7 7 0 0 1 7 7Z'
                fill='none'
                stroke='currentColor'
                strokeWidth='2'
                strokeLinejoin='round'
              />
            </svg>
            <svg className='toggle-icon chevron' viewBox='0 0 24 24' aria-hidden='true'>
              <path
                d='M15 18l-6-6 6-6'
                fill='none'
                stroke='currentColor'
                strokeWidth='2'
                strokeLinecap='round'
                strokeLinejoin='round'
              />
            </svg>
          </button>

          <div className='chat-content'>
            <header className='chat-header'>
              <div>
                <h2>Conversation</h2>
                <p className='muted'>Historique complet, toujours visible.</p>
              </div>
              <div className='mode-toggle' role='group' aria-label='Mode'>
                <button
                  type='button'
                  className={`mode-btn ${mode === 'shapes' ? 'active' : ''}`}
                  onClick={() => setMode('shapes')}
                >
                  Shapes
                </button>
                <button
                  type='button'
                  className={`mode-btn ${mode === 'functions' ? 'active' : ''}`}
                  onClick={() => setMode('functions')}
                >
                  Functions
                </button>
              </div>
            </header>

          <div className='chat-body'>
            {messages.length === 0 ? (
              <div className='empty'>
                <p>Start by describing a shape on the right.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div
                    className={`bubble ${message.status === 'error' ? 'error' : ''} ${message.id === activeMessage?.id ? 'active' : ''} ${message.shapes?.length ? 'clickable' : ''}`}
                    role={message.shapes?.length ? 'button' : undefined}
                    tabIndex={message.shapes?.length ? 0 : undefined}
                    onClick={() => {
                      if (message.shapes?.length) {
                        setActiveMessageId(message.id);
                        setActiveIndex(0);
                      }
                    }}
                    onKeyDown={(event) => {
                      if (
                        message.shapes?.length &&
                        (event.key === 'Enter' || event.key === ' ')
                      ) {
                        event.preventDefault();
                        setActiveMessageId(message.id);
                        setActiveIndex(0);
                      }
                    }}
                  >
                    <p className='message-text'>{message.text}</p>
                    {message.shapeCount > 0 && (
                      <span className='meta'>
                        {message.shapeCount} shape(s) generated
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
            <div ref={endRef} />
          </div>

          <form ref={formRef} className='composer' onSubmit={handleSubmit}>
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={placeholder}
              rows={3}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  formRef.current?.requestSubmit();
                }
              }}
            />
            <div className='composer-actions'>
              <div className='examples'>
                {examples.map((example) => (
                  <button
                    key={example}
                    type='button'
                    className='chip'
                    onClick={() => setInput(example)}
                  >
                    {example}
                  </button>
                ))}
              </div>
              <button className='primary' type='submit' disabled={!canSend}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </form>
          </div>
        </div>
      </section>

      <section className='panel assistant-panel'>
        <header className='panel-header'>
          <div>
            <p className='eyebrow'>ShapeIA</p>
            <h1>3D Geometry Assistant</h1>
            <p className='muted'>
              Visualisation, calculs et formules en un seul endroit.
            </p>
          </div>
          <div className='status-pill'>{loading ? 'Thinking...' : 'Ready'}</div>
        </header>

        <div className='panel-scroll'>
          <div className='shape-tabs'>
            {activeShapes.length === 0 && (
              <span className='tab muted'>No shape yet</span>
            )}
            {activeShapes.map((shape, index) => (
              <button
                key={`${shape.name}-${index}`}
                type='button'
                className={`tab ${index === activeIndex ? 'active' : ''}`}
                onClick={() => setActiveIndex(index)}
              >
                {shape.name}
              </button>
            ))}
          </div>

          <div className='geometry-grid'>
            <div className='plot-card'>
              <div className='plot-inner'>
                {plotProps ? (
                  <Plot
                    data={plotProps.data}
                    layout={plotProps.layout}
                    config={plotProps.config}
                    useResizeHandler
                    style={{ width: '100%', height: '100%' }}
                  />
                ) : (
                  <div className='plot-empty'>
                    <p>Send a command to generate a shape.</p>
                  </div>
                )}
              </div>
            </div>

            <div className='info-stack'>
              <div className='detail-card calc-card'>
                <h3>Calculations</h3>
                {Object.keys(activeShape?.calculations || {}).length === 0 ? (
                  <p className='muted'>No calculations available.</p>
                ) : (
                  <div className='metric-grid'>
                    {Object.entries(activeShape.calculations).map(
                      ([key, value]) => (
                        <div className='metric' key={key}>
                          <span>{key}</span>
                          <strong>{value}</strong>
                        </div>
                      )
                    )}
                  </div>
                )}
              </div>

              <div className='detail-card formula-card'>
                <h3>Formulas</h3>
                {Object.keys(activeShape?.formulas || {}).length === 0 ? (
                  <p className='muted'>No formulas available.</p>
                ) : (
                  <div className='formula-list'>
                    {Object.entries(activeShape.formulas).map(([key, value]) => (
                      <div className='formula' key={key}>
                        <span>{key}</span>
                        <div className='formula-latex'>
                          <BlockMath
                            math={value}
                            renderError={() => (
                              <span className='latex-error'>{value}</span>
                            )}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
