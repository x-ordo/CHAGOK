import React from 'react';
import { X, BookOpen, AlertTriangle, Scale } from 'lucide-react';

interface ExpertInsightsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ExpertInsightsPanel({ isOpen, onClose }: ExpertInsightsPanelProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4 sm:p-6">
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity" 
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-2xl bg-white dark:bg-neutral-800 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-900/50">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-[var(--color-primary-light)] rounded-lg">
              <BookOpen className="w-5 h-5 text-[var(--color-primary)]" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-[var(--color-text-primary)]">전문가 인사이트</h2>
              <p className="text-xs text-[var(--color-text-secondary)]">이혼 소송 주요 법리 및 실무 가이드</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Section 1: Property Division */}
          <section className="space-y-3">
            <div className="flex items-center gap-2 text-[var(--color-secondary)] dark:text-[var(--color-text-primary)]">
              <Scale className="w-5 h-5" />
              <h3 className="font-semibold text-lg">재산분할 원칙 (판례)</h3>
            </div>
            
            <div className="bg-[var(--color-neutral-50)] dark:bg-neutral-900/30 rounded-lg p-4 border border-[var(--color-neutral-200)] dark:border-neutral-700 text-sm space-y-3">
              <div>
                <strong className="text-[var(--color-text-primary)] block mb-1">특유재산의 처리</strong>
                <p className="text-[var(--color-text-secondary)]">
                  상속·증여받은 특유재산은 원칙적으로 분할 대상에서 제외됩니다. 
                  단, <span className="text-[var(--color-primary)] font-medium">배우자가 그 재산의 유지나 증식에 
                  기여했음이 입증되는 경우</span>에는 예외적으로 분할 대상에 포함될 수 있습니다.
                </p>
              </div>
              
              <div className="pt-3 border-t border-[var(--color-neutral-200)] dark:border-neutral-700">
                <strong className="text-[var(--color-text-primary)] block mb-1">퇴직금 및 연금</strong>
                <p className="text-[var(--color-text-secondary)]">
                  이미 수령한 퇴직금/연금뿐만 아니라, <span className="text-[var(--color-primary)] font-medium">
                  장래에 수령할 퇴직급여</span>도 변론종결 시점에 경제적 가치 평가가 가능하다면 분할 대상에 포함됩니다.
                </p>
              </div>

               <div className="pt-3 border-t border-[var(--color-neutral-200)] dark:border-neutral-700">
                <strong className="text-[var(--color-text-primary)] block mb-1">사해행위 취소권</strong>
                <p className="text-[var(--color-text-secondary)]">
                  재산분할청구권을 보전하기 위한 사해행위 취소권은 
                  <span className="text-[var(--color-error)] font-medium ml-1">
                    취소원인을 안 날로부터 1년, 법률행위가 있은 날로부터 5년
                  </span> 내에 행사해야 합니다.
                </p>
              </div>
            </div>
          </section>

          {/* Section 2: Tax Implications */}
          <section className="space-y-3">
            <div className="flex items-center gap-2 text-[var(--color-secondary)] dark:text-[var(--color-text-primary)]">
              <AlertTriangle className="w-5 h-5 text-[var(--color-warning)]" />
              <h3 className="font-semibold text-lg">세무/행정 유의사항</h3>
            </div>
            
            <div className="bg-orange-50 dark:bg-orange-900/10 rounded-lg p-4 border border-orange-100 dark:border-orange-800 text-sm space-y-3">
               <div>
                <strong className="text-orange-900 dark:text-orange-200 block mb-1">위자료 vs 재산분할 세금 차이</strong>
                <ul className="list-disc pl-4 space-y-1 text-orange-800 dark:text-orange-300/80">
                  <li>
                    <span className="font-medium">재산분할:</span> 원칙적으로 <span className="text-[var(--color-success)]">증여세/소득세 비과세</span> (취득세는 발생 가능).
                  </li>
                  <li>
                    <span className="font-medium">위자료:</span> 조세법상 소득으로 보지 않으나, 부동산으로 대물변제 시 양도소득세가 부과될 수 있으므로 <span className="font-bold underline decoration-orange-400">반드시 세무 검토가 필요합니다.</span>
                  </li>
                </ul>
              </div>

              <div className="pt-3 border-t border-orange-200 dark:border-orange-800/50">
                <strong className="text-orange-900 dark:text-orange-200 block mb-1">이혼신고 지연 과태료</strong>
                <p className="text-orange-800 dark:text-orange-300/80">
                  재판상 이혼의 경우, 판결 확정일로부터 1개월 이내에 신고하지 않으면 과태료가 부과됩니다.
                </p>
              </div>
            </div>
          </section>

        </div>
        
        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-100 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-900/50 text-xs text-[var(--color-text-tertiary)] flex justify-between items-center">
             <span>Referenced from: 2024 Household Litigation Guide</span>
             <button 
               onClick={onClose}
               className="px-4 py-2 bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-600 rounded-lg hover:bg-gray-50 dark:hover:bg-neutral-700 transition-colors font-medium text-[var(--color-text-primary)]"
             >
               닫기
             </button>
        </div>
      </div>
    </div>
  );
}

export default ExpertInsightsPanel;
