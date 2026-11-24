#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轻量 CRF 层：前向算法（训练）+ 维特比解码（推理），仅依赖 PyTorch。"""
from __future__ import annotations

import torch
import torch.nn as nn


class CRF(nn.Module):
    def __init__(self, num_tags: int):
        super().__init__()
        self.num_tags = num_tags
        self.transitions = nn.Parameter(torch.randn(num_tags, num_tags) * 0.1)
        self.start_transitions = nn.Parameter(torch.randn(num_tags) * 0.1)
        self.end_transitions = nn.Parameter(torch.randn(num_tags) * 0.1)

    def _log_sum_exp(self, scores: torch.Tensor, dim: int) -> torch.Tensor:
        max_score, _ = scores.max(dim=dim)
        return max_score + (scores - max_score.unsqueeze(dim)).exp().sum(dim).log()

    def forward(self, emissions: torch.Tensor, tags: torch.Tensor,
                mask: torch.Tensor | None = None) -> torch.Tensor:
        """返回批次的负对数似然（越小越好）。emissions: [B, L, T]"""
        if mask is None:
            mask = torch.ones(emissions.size()[:2], dtype=torch.bool, device=emissions.device)
        total = 0.0
        for emission, tag, m in zip(emissions, tags, mask):
            length = int(m.sum())
            e, t = emission[:length], tag[:length]
            score = self.start_transitions[t[0]] + e[0, t[0]]
            for i in range(1, length):
                score = score + self.transitions[t[i - 1], t[i]] + e[i, t[i]]
            score = score + self.end_transitions[t[-1]]
            # 配分函数（前向算法）
            alpha = self.start_transitions + e[0]
            for i in range(1, length):
                alpha = self._log_sum_exp(
                    alpha.unsqueeze(-1) + self.transitions.unsqueeze(0), dim=1
                ) + e[i]
            partition = self._log_sum_exp(alpha + self.end_transitions, dim=0)
            total = total + (partition - score)
        return total / emissions.size(0)

    def decode(self, emissions: torch.Tensor,
               mask: torch.Tensor | None = None) -> list[list[int]]:
        """维特比解码，返回每条序列的最优标签索引列表。"""
        if mask is None:
            mask = torch.ones(emissions.size()[:2], dtype=torch.bool, device=emissions.device)
        results = []
        for emission, m in zip(emissions, mask):
            length = int(m.sum())
            e = emission[:length]
            score = self.start_transitions.unsqueeze(0) + e[0].unsqueeze(0)
            history = []
            for i in range(1, length):
                scores = score.unsqueeze(-1) + self.transitions.unsqueeze(0)
                best, idx = scores.max(dim=1)
                history.append(idx)
                score = best + e[i].unsqueeze(0)
            score = score + self.end_transitions.unsqueeze(0)
            _, best_last = score.max(dim=1)
            best_path = [int(best_last[0])]
            for idx in reversed(history):
                best_path.append(int(idx[0, best_path[-1]]))
            best_path.reverse()
            results.append(best_path)
        return results
