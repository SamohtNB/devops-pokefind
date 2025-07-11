// frontend/src/App.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

describe('<App />', () => {
  beforeAll(() => {
    // Mock URL.createObjectURL pour fournir une URL fixe pour l’aperçu
    global.URL.createObjectURL = jest.fn(() => 'preview-url');
  });

  beforeEach(() => {
    jest.restoreAllMocks();
  });

  it('rend l’input file et le bouton Prédire désactivé au départ', () => {
    const { container } = render(<App />);
    const fileInput = container.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();

    const predictBtn = screen.getByRole('button', { name: /prédire/i });
    expect(predictBtn).toBeDisabled();
  });

  it('affiche le résultat de la prédiction après un fetch réussi', async () => {
    // Mock de fetch pour un succès
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pokemon: 'pikachu' }),
    });

    const { container } = render(<App />);
    const fileInput = container.querySelector('input[type="file"]');
    const file = new File(['img'], 'pikachu.png', { type: 'image/png' });
    await userEvent.upload(fileInput, file);

    const predictBtn = screen.getByRole('button', { name: /prédire/i });
    userEvent.click(predictBtn);

    // Vérifier l’état de chargement
    expect(predictBtn).toHaveTextContent(/chargement/i);
    expect(predictBtn).toBeDisabled();

    // Attendre l’affichage du résultat
    await waitFor(() => {
      expect(screen.getByText(/il s'agit de : pikachu/i)).toBeInTheDocument();
    });
  });

  it('affiche un message d’erreur quand le fetch échoue', async () => {
    // Mock de fetch pour un échec
    global.fetch = jest.fn().mockResolvedValueOnce({ ok: false, status: 500 });

    const { container } = render(<App />);
    const fileInput = container.querySelector('input[type="file"]');
    const file = new File(['img'], 'error.png', { type: 'image/png' });
    await userEvent.upload(fileInput, file);

    const predictBtn = screen.getByRole('button', { name: /prédire/i });
    userEvent.click(predictBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/impossible de contacter le service de prédiction/i)
      ).toBeInTheDocument();
    });
  });
});
