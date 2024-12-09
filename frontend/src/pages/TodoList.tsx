import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { Todo } from '../types/todo';

export function TodoList() {
  const { token } = useAuth();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      loadTodos();
    }
  }, [token]);

  const loadTodos = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const data = await api.todos.getAll(token);
      setTodos(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load todos');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !newTodoTitle.trim()) return;

    setIsLoading(true);
    try {
      const newTodo = await api.todos.create(token, { title: newTodoTitle.trim() });
      setTodos(prev => [...prev, newTodo]);
      setNewTodoTitle('');
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add todo');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleTodo = async (todo: Todo) => {
    if (!token) return;

    setIsLoading(true);
    try {
      const updatedTodo = await api.todos.update(token, todo.id, {
        completed: !todo.completed,
      });
      setTodos(prev =>
        prev.map(t => (t.id === updatedTodo.id ? updatedTodo : t))
      );
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update todo');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTodo = async (id: number) => {
    if (!token) return;

    setIsLoading(true);
    try {
      await api.todos.delete(token, id);
      setTodos(prev => prev.filter(t => t.id !== id));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete todo');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !todos.length) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Todo List</h1>

      <form onSubmit={handleAddTodo} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={newTodoTitle}
            onChange={e => setNewTodoTitle(e.target.value)}
            placeholder="Add a new todo..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !newTodoTitle.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Add
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">{error}</div>
      )}

      <ul className="space-y-4">
        {todos.map(todo => (
          <li
            key={todo.id}
            className="flex items-center gap-4 p-4 bg-white rounded-lg shadow"
          >
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => handleToggleTodo(todo)}
              className="w-5 h-5 text-blue-500"
            />
            <span
              className={`flex-1 ${
                todo.completed ? 'line-through text-gray-500' : ''
              }`}
            >
              {todo.title}
            </span>
            <button
              onClick={() => handleDeleteTodo(todo.id)}
              className="p-2 text-red-500 hover:text-red-700 focus:outline-none"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      {!isLoading && !todos.length && (
        <p className="text-center text-gray-500">No todos yet. Add one above!</p>
      )}
    </div>
  );
} 